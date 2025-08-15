from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from .models import PricelistItem
from django.db import models


UNIT_TO_HOURS = {
	'hour': 1,
	'day': 24,
	'week': 24 * 7,
	'month': 24 * 30,
	'year': 24 * 365,
}


def normalize_duration_to_unit(start_at, end_at, unit: str) -> int:
	delta: timedelta = end_at - start_at
	hours = Decimal(delta.total_seconds()) / Decimal(3600)
	unit_hours = Decimal(UNIT_TO_HOURS[unit])
	# Round up to next whole unit
	qty = (hours + unit_hours - 1) // unit_hours
	return int(qty)


def find_applicable_item(product, unit: str, duration_qty: int, on_date=None):
	qs = PricelistItem.objects.filter(
		active_pricelist=True,
		unit=unit,
	).filter(
		models.Q(product=product) | models.Q(product__isnull=True, category=product.category)
	)
	if on_date is None:
		on_date = timezone.now().date()
	qs = qs.filter(
		models.Q(pricelist__valid_from__isnull=True) | models.Q(pricelist__valid_from__lte=on_date),
		models.Q(pricelist__valid_to__isnull=True) | models.Q(pricelist__valid_to__gte=on_date),
	)
	qs = qs.order_by('priority')
	for item in qs:
		if item.max_duration and duration_qty > item.max_duration:
			continue
		if duration_qty < item.min_duration:
			continue
		return item
	return None


def compute_line_price(product, start_at, end_at, unit: str):
	duration_qty = normalize_duration_to_unit(start_at, end_at, unit)
	item = None
	# Simple: try requested unit; extension to tiered/best-fit can be added later
	item = PricelistItem.objects.filter(
		pricelist__active=True,
		unit=unit,
	).filter(
		(models.Q(product=product)) | (models.Q(product__isnull=True, category=product.category))
	).order_by('priority').first()
	if not item:
		return {'unit_price': Decimal('0'), 'duration_qty': duration_qty, 'subtotal': Decimal('0'), 'rule': ''}

	price = item.base_price
	if item.discount_type == 'percent' and item.discount_value:
		price = price * (Decimal('1') - (item.discount_value / Decimal('100')))
	elif item.discount_type == 'fixed' and item.discount_value:
		price = price - item.discount_value
	price = price.quantize(Decimal('0.01'))
	subtotal = (price * Decimal(duration_qty)).quantize(Decimal('0.01'))
	return {
		'unit_price': price,
		'duration_qty': duration_qty,
		'subtotal': subtotal,
		'rule': f"{unit}@{price}",
	}
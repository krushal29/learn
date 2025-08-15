from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from catalog.models import Product


class RentalOrder(models.Model):
	STATUS_CHOICES = [
		('draft', 'Draft'),
		('quoted', 'Quoted'),
		('confirmed', 'Confirmed'),
		('out', 'Out'),
		('returned', 'Returned'),
		('invoiced', 'Invoiced'),
		('closed', 'Closed'),
		('cancelled', 'Cancelled'),
	]
	number = models.CharField(max_length=40, unique=True, blank=True)
	customer_name = models.CharField(max_length=255)
	customer_email = models.EmailField(blank=True)
	status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='draft')
	start_at = models.DateTimeField()
	end_at = models.DateTimeField()
	expected_return_at = models.DateTimeField(null=True, blank=True)
	actual_return_at = models.DateTimeField(null=True, blank=True)
	total_rent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	deposit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	taxes_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	fees_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	currency = models.CharField(max_length=3, default='USD')
	payment_status = models.CharField(max_length=20, default='unpaid')
	contract_url = models.URLField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self) -> str:
		return self.number or f"Order {self.pk}"

	def save(self, *args, **kwargs):
		if not self.number:
			date_str = timezone.now().strftime('%Y%m%d')
			prefix = f"RO-{date_str}-"
			last = RentalOrder.objects.filter(number__startswith=prefix).order_by('-number').first()
			next_seq = 1
			if last and last.number:
				try:
					next_seq = int(last.number.split('-')[-1]) + 1
				except Exception:
					next_seq = 1
			self.number = f"{prefix}{next_seq:04d}"
		if not self.expected_return_at:
			self.expected_return_at = self.end_at
		super().save(*args, **kwargs)

	def recalculate_totals(self):
		lines = list(self.lines.all())
		total = sum([line.subtotal for line in lines], Decimal('0'))
		self.total_rent = total
		self.save(update_fields=['total_rent'])


class RentalOrderLine(models.Model):
	order = models.ForeignKey(RentalOrder, on_delete=models.CASCADE, related_name='lines')
	product = models.ForeignKey(Product, on_delete=models.PROTECT)
	quantity = models.PositiveIntegerField(default=1)
	unit = models.CharField(max_length=10, default='day')
	duration_qty = models.PositiveIntegerField(default=1)
	unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	rule_applied = models.CharField(max_length=255, blank=True)
	subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

	def __str__(self) -> str:
		return f"{self.order.number} - {self.product.name}"


class Reservation(models.Model):
	STATUS_CHOICES = [
		('reserved', 'Reserved'),
		('collected', 'Collected'),
		('returned', 'Returned'),
		('expired', 'Expired'),
	]
	product = models.ForeignKey(Product, on_delete=models.PROTECT)
	order_line = models.ForeignKey(RentalOrderLine, on_delete=models.CASCADE, related_name='reservations')
	start_at = models.DateTimeField()
	end_at = models.DateTimeField()
	quantity = models.PositiveIntegerField(default=1)
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='reserved')
	allocated_serials = models.JSONField(default=list, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		indexes = [
			models.Index(fields=['product', 'start_at', 'end_at']),
		]


class Delivery(models.Model):
	DOC_TYPE = [
		('pickup', 'Pickup'),
		('return', 'Return'),
	]
	document_type = models.CharField(max_length=10, choices=DOC_TYPE)
	order = models.ForeignKey(RentalOrder, on_delete=models.CASCADE, related_name='deliveries')
	scheduled_at = models.DateTimeField()
	items = models.JSONField(default=list)
	status = models.CharField(max_length=20, default='pending')
	damage_notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

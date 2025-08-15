from django.db import models
from catalog.models import Product


class Pricelist(models.Model):
	name = models.CharField(max_length=120)
	currency = models.CharField(max_length=3, default='USD')
	customer_group = models.CharField(max_length=120, blank=True)
	region = models.CharField(max_length=120, blank=True)
	valid_from = models.DateField(null=True, blank=True)
	valid_to = models.DateField(null=True, blank=True)
	active = models.BooleanField(default=True)

	class Meta:
		ordering = ['name']

	def __str__(self) -> str:
		return self.name


class PricelistItem(models.Model):
	UNIT_CHOICES = [
		('hour', 'Hour'),
		('day', 'Day'),
		('week', 'Week'),
		('month', 'Month'),
		('year', 'Year'),
	]
	pricelist = models.ForeignKey(Pricelist, on_delete=models.CASCADE, related_name='items')
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='pricelist_items', null=True, blank=True)
	category = models.CharField(max_length=120, blank=True)
	unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='day')
	base_price = models.DecimalField(max_digits=12, decimal_places=2)
	min_duration = models.PositiveIntegerField(default=1)
	max_duration = models.PositiveIntegerField(null=True, blank=True)
	discount_type = models.CharField(max_length=10, choices=[('percent','Percent'),('fixed','Fixed')], blank=True)
	discount_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
	priority = models.IntegerField(default=10)

	class Meta:
		ordering = ['priority', 'id']

	def __str__(self) -> str:
		return f"{self.pricelist.name} - {self.product or self.category} ({self.unit})"

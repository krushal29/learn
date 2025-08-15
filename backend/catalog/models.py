from django.db import models


class Product(models.Model):
	UNIT_CHOICES = [
		('hour', 'Hour'),
		('day', 'Day'),
		('week', 'Week'),
		('month', 'Month'),
		('year', 'Year'),
	]
	LATE_FEE_TYPE = [
		('fixed', 'Fixed'),
		('per_unit', 'Per Unit Time'),
	]
	TRACKING_MODE = [
		('none', 'None'),
		('serial', 'Serial Tracked'),
	]

	name = models.CharField(max_length=255)
	category = models.CharField(max_length=120, blank=True)
	is_rentable = models.BooleanField(default=True)
	stock_quantity = models.PositiveIntegerField(default=0)
	tracking_mode = models.CharField(max_length=10, choices=TRACKING_MODE, default='none')
	rental_units = models.CharField(max_length=10, choices=UNIT_CHOICES, default='day')
	min_duration = models.PositiveIntegerField(default=1)
	max_duration = models.PositiveIntegerField(null=True, blank=True)
	buffer_before_hours = models.PositiveIntegerField(default=0)
	buffer_after_hours = models.PositiveIntegerField(default=0)
	deposit_required = models.BooleanField(default=False)
	deposit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	late_fee_type = models.CharField(max_length=10, choices=LATE_FEE_TYPE, default='per_unit')
	late_fee_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='day')
	late_fee_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['name']

	def __str__(self) -> str:
		return self.name

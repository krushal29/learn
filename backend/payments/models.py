from django.db import models
from rentals.models import RentalOrder


class Payment(models.Model):
	GATEWAY_CHOICES = [
		('stripe', 'Stripe'),
		('paypal', 'PayPal'),
		('razorpay', 'Razorpay'),
	]
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('authorized', 'Authorized'),
		('captured', 'Captured'),
		('failed', 'Failed'),
		('refunded', 'Refunded'),
	]
	order = models.ForeignKey(RentalOrder, on_delete=models.CASCADE, related_name='payments')
	gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES, default='stripe')
	intent_id = models.CharField(max_length=120, blank=True)
	charge_id = models.CharField(max_length=120, blank=True)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	currency = models.CharField(max_length=3, default='USD')
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
	is_deposit = models.BooleanField(default=False)
	metadata = models.JSONField(default=dict, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

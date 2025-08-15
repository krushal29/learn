from django.db import models

# Create your models here.


class NotificationSetting(models.Model):
	lead_days_customer = models.PositiveIntegerField(default=2)
	lead_days_end_user = models.PositiveIntegerField(default=2)
	email_template_customer = models.TextField(blank=True)
	email_template_end_user = models.TextField(blank=True)
	active = models.BooleanField(default=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return f"Notifications (customer {self.lead_days_customer}d, end-user {self.lead_days_end_user}d)"

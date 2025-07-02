from django.db import models

from apps.master_data.models import SubDepartment
from apps.meta_app.models import MyBaseModel
from user_details.models import User


class Subscription(models.Model):
    # Basic info for the subscription
    duration_choices = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    name = models.CharField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    duration = models.CharField(max_length=10, choices=duration_choices)
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sub_department = models.ManyToManyField(SubDepartment, related_name="subscription_subscription_master")

    def __str__(self):
        return f"{self.name} - {self.price} {self.currency} ({self.duration})"


class Transaction(MyBaseModel):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('authorized', 'Authorized'),
        ('captured', 'Captured'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partial_refunded', 'Partially Refunded'),
        ('success', 'Success'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    amount = models.FloatField()
    currency = models.CharField(max_length=10, default="INR")
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return f"{self.user} - {self.razorpay_order_id} - {self.status}"

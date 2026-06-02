from django.db import models
from apps.finance.models import FeeInvoice

class MpesaTransaction(models.Model):
    merchant_request_id = models.CharField(max_length=100, unique=True)
    checkout_request_id = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.SET_NULL, null=True, blank=True)   # New field
    status = models.CharField(max_length=20, default='pending') # pending, completed, failed
    result_code = models.CharField(max_length=10, blank=True, null=True)
    result_desc = models.CharField(max_length=255, blank=True, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    payment = models.OneToOneField('finance.Payment', on_delete=models.SET_NULL, null=True, blank=True)  # Link to created payment

    def __str__(self):
        return f"{self.phone_number} - {self.amount}"
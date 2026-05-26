from django.db import models
from apps.common.models import BaseModel, SoftDeleteModel
from django.utils import timezone

class FeeInvoice(SoftDeleteModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'), ('sent', 'Sent'), ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'), ('overdue', 'Overdue'), ('cancelled', 'Cancelled')
    ]
    invoice_number = models.CharField(max_length=50, unique=True)
    student = models.ForeignKey('core.Student', on_delete=models.RESTRICT, related_name='invoices')
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.RESTRICT)
    term = models.ForeignKey('academics.Term', on_delete=models.RESTRICT, null=True, blank=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('core.Staff', on_delete=models.RESTRICT, related_name='created_invoices')

    @property
    def balance_due(self):
        return self.total_amount - self.paid_amount

    def __str__(self):
        return f"{self.invoice_number} - {self.student}"

class InvoiceLineItem(BaseModel):
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.CASCADE, related_name='line_items')
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=50, blank=True)
    is_lost_book = models.BooleanField(default=False)
    book_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.invoice.invoice_number}: {self.description}"

class Payment(BaseModel):
    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'), ('airtel', 'Airtel Money'), ('tkash', 'T-Kash'),
        ('equity', 'Equity'), ('kcb', 'KCB'), ('coop', 'Co-op'), ('absa', 'ABSA'),
        ('stanbic', 'Stanbic'), ('scb', 'Standard Chartered'), ('dtb', 'DTB'),
        ('ncba', 'NCBA'), ('family', 'Family Bank'), ('im', 'I&M Bank'),
        ('cash', 'Cash'), ('cheque', 'Cheque')
    ]
    CHANNEL_CHOICES = [('stk', 'STK Push'), ('bank_transfer', 'Bank Transfer'), ('manual', 'Manual Entry')]
    STATUS_CHOICES = [('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')]

    transaction_reference = models.CharField(max_length=100, unique=True)
    student = models.ForeignKey('core.Student', on_delete=models.RESTRICT, related_name='payments')
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    mpesa_receipt = models.CharField(max_length=50, blank=True)
    recorded_by = models.ForeignKey('core.Staff', on_delete=models.RESTRICT, related_name='recorded_payments')
    payment_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.transaction_reference} - {self.student}"

class PaymentAllocation(BaseModel):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='allocations')
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.CASCADE)
    amount_allocated = models.DecimalField(max_digits=12, decimal_places=2)

class ExpenseCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Expense(SoftDeleteModel):
    STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('paid', 'Paid'), ('partially_paid', 'Partially Paid'), ('rejected', 'Rejected')]
    expense_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.RESTRICT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payee_name = models.CharField(max_length=200)
    payee_phone = models.CharField(max_length=15, blank=True)
    payee_bank = models.CharField(max_length=50, blank=True)
    payee_account = models.CharField(max_length=50, blank=True)
    expense_date = models.DateField()
    created_by = models.ForeignKey('core.Staff', on_delete=models.RESTRICT, related_name='expenses_created')
    approved_by = models.ForeignKey('core.Staff', on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses_approved')
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

class ExpensePayment(BaseModel):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=[('b2c', 'M-Pesa B2C'), ('b2b', 'M-Pesa B2B'), ('bank', 'Bank Transfer'), ('cash', 'Cash'), ('cheque', 'Cheque')])
    transaction_reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='processing')
    processed_by = models.ForeignKey('core.Staff', on_delete=models.RESTRICT, related_name='expense_payments')
    processed_at = models.DateTimeField(default=timezone.now)
    mpesa_receipt = models.CharField(max_length=50, blank=True)
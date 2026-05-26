from django.db import models
from apps.common.models import BaseModel

class APIKey(BaseModel):
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True)
    client_system = models.CharField(max_length=100)  # e.g., 'LMS'
    permissions = models.JSONField()  # e.g., ['students:read', 'lost_books:create']
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey('core.Staff', on_delete=models.RESTRICT, related_name='api_keys')

    def __str__(self):
        return self.name

class LostBookEvent(BaseModel):
    SYNC_STATUS = [('pending', 'Pending'), ('synced', 'Synced'), ('failed', 'Failed')]
    student = models.ForeignKey('core.Student', on_delete=models.RESTRICT, related_name='lost_book_events')
    book_number = models.CharField(max_length=50)
    book_title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.RESTRICT)
    term = models.ForeignKey('academics.Term', on_delete=models.RESTRICT)
    loss_date = models.DateField()
    fee_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    invoice_line_item = models.ForeignKey('finance.InvoiceLineItem', on_delete=models.SET_NULL, null=True, blank=True)
    is_cleared = models.BooleanField(default=False)
    cleared_at = models.DateTimeField(null=True, blank=True)
    lms_sync_status = models.CharField(max_length=20, choices=SYNC_STATUS, default='pending')

    def __str__(self):
        return f"{self.book_number} - {self.student}"
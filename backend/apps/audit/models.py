from django.db import models
from apps.common.models import BaseModel

class AuditLog(BaseModel):
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    user_role = models.CharField(max_length=50, blank=True)
    action = models.CharField(max_length=50)  # CREATE, UPDATE, DELETE, APPROVE, PAY, etc.
    table_name = models.CharField(max_length=100)
    record_id = models.UUIDField()
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} on {self.table_name} by {self.user} at {self.created_at}"
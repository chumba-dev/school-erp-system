from django.db import models
from apps.common.models import BaseModel

class AuditLog(BaseModel):
    user_id = models.UUIDField(null=True, blank=True)
    user_role = models.CharField(max_length=50, blank=True)
    action = models.CharField(max_length=50)
    table_name = models.CharField(max_length=100)
    record_id = models.UUIDField()
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.action} on {self.table_name} at {self.created_at}"
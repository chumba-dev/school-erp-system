from django.db import models
from apps.common.models import BaseModel
from apps.core.models import Staff

class School(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, unique=True)  # e.g., 'KIT'
    subdomain = models.CharField(max_length=50, unique=True, blank=True)  # e.g., 'kitondo'
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    logo = models.ImageField(upload_to='school_logos/', null=True, blank=True)
    website = models.URLField(blank=True)
    motto = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    subscription_expiry = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_schools')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
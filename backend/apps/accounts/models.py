from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.common.models import BaseModel

class User(AbstractUser, BaseModel):
    # Override groups and user_permissions to avoid reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts_user_set',   # unique related name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts_user_set',   # unique related name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    ROLE_CHOICES = [
        ('bursar', 'Bursar'),
        ('admin', 'Admin'),
        ('principal', 'Principal'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='parent')
    staff_profile = models.OneToOneField('core.Staff', on_delete=models.SET_NULL, null=True, blank=True, related_name='user')
    student_profile = models.OneToOneField('core.Student', on_delete=models.SET_NULL, null=True, blank=True, related_name='user')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
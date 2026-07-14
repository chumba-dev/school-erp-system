from django.db import models
from apps.common.models import BaseModel
from apps.accounts.models import User
from apps.core.models import Student

class ParentStudent(BaseModel):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='children')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='parents')
    is_primary = models.BooleanField(default=False)
    relationship = models.CharField(max_length=50, blank=True)  # e.g., 'Father', 'Mother', 'Guardian'

    class Meta:
        unique_together = ('parent', 'student')

    def __str__(self):
        return f"{self.parent.username} - {self.student.admission_number}"
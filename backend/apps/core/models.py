from django.apps import AppConfig
from django.db import models
from django.utils import timezone

from ..common.models import BaseModel, SoftDeleteModel   # import from common
#from apps.academics.models import Class, AcademicYear, Term
class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.common'

class Department(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Staff(SoftDeleteModel):
    TENURE_CHOICES = [
        ('Permanent', 'Permanent'),
        ('Contract', 'Contract'),
    ]
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Retired', 'Retired'),
        ('Transferred', 'Transferred'),
        ('Closed', 'Closed'),
    ]
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, null=True, blank=True)
    tsc_number = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    tenure_type = models.CharField(max_length=20, choices=TENURE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    phone = models.CharField(max_length=15)
    bank_name = models.CharField(max_length=50, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
   

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.tsc_number})"


class Student(SoftDeleteModel):
    CBC_PATHWAY_CHOICES = [
        ('STEM', 'STEM'),
        ('Arts & Sports Science', 'Arts & Sports Science'),
        ('Social Sciences', 'Social Sciences'),
    ]
    ENROLLMENT_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Graduated', 'Graduated'),
        ('Transferred', 'Transferred'),
        ('Suspended', 'Suspended'),
    ]
    admission_number = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    parent_name = models.CharField(max_length=200)
    parent_phone = models.CharField(max_length=15)
    parent_email = models.EmailField(max_length=100, blank=True)
    class_obj = models.ForeignKey('academics.Class', on_delete=models.RESTRICT, related_name='students', db_column='class_id')
    stream = models.ForeignKey('academics.Stream', on_delete=models.RESTRICT, related_name='students', db_column='stream_id')
    cbc_pathway = models.CharField(max_length=50, choices=CBC_PATHWAY_CHOICES, blank=True, null=True)
    enrollment_status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS_CHOICES, default='Active')
    registration_date = models.DateField(default=timezone.now)
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.admission_number})"
    
    ACADEMIC_STATUS_CHOICES = [
        ('active', 'Active'),
        ('promoted', 'Promoted'),
        ('graduated', 'Graduated'),
        ('repeated', 'Repeated'),
        ('transferred', 'Transferred'),
    ]
    academic_status = models.CharField(max_length=20, choices=ACADEMIC_STATUS_CHOICES, default='active')
    current_class = models.ForeignKey('academics.Class', on_delete=models.SET_NULL, null=True, blank=True)  # if not using class_obj? We'll rename later.

class AcademicHistory(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='academic_history')
    class_obj = models.ForeignKey('academics.Class', on_delete=models.PROTECT)
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.PROTECT)
    term = models.ForeignKey('academics.Term', on_delete=models.PROTECT, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Student.ACADEMIC_STATUS_CHOICES)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student} - {self.class_obj} ({self.academic_year})"

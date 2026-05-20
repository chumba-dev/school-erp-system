from django.db import models
from apps.common.models import BaseModel

class AcademicYear(BaseModel):
    year = models.IntegerField(unique=True)
    is_current = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return str(self.year)


class Term(BaseModel):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='terms')
    term_number = models.IntegerField()
    name = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        unique_together = ['academic_year', 'term_number']

    def __str__(self):
        return f"{self.academic_year.year} - {self.name}"


class Class(BaseModel):
    CURRICULUM_CHOICES = [('844', '8-4-4'), ('CBC', 'CBC')]
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    curriculum = models.CharField(max_length=3, choices=CURRICULUM_CHOICES)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Stream(BaseModel):
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='streams', db_column='class_id')
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        unique_together = ['class_obj', 'name']

    def __str__(self):
        return f"{self.class_obj.name} - {self.name}"


class Subject(BaseModel):
    department = models.ForeignKey('core.Department', on_delete=models.RESTRICT, related_name='subjects')
    name = models.CharField(max_length=100)
    cbc_pathway = models.CharField(max_length=50, choices=[
        ('STEM', 'STEM'),
        ('Arts & Sports Science', 'Arts & Sports Science'),
        ('Social Sciences', 'Social Sciences'),
    ], blank=True, null=True)
    code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class StaffSubject(BaseModel):
    staff = models.ForeignKey('core.Staff', on_delete=models.CASCADE, related_name='subjects_taught')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='staff_teaching')

    class Meta:
        unique_together = ['staff', 'subject']

    def __str__(self):
        return f"{self.staff} teaches {self.subject}"
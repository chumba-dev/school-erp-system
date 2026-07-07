from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.models import BaseModel
from apps.schools.models import School
from apps.academics.models import AcademicYear, Term, Class, Stream, Subject
from apps.core.models import Student, Staff

class GradeScale(BaseModel):
    """Defines grading scheme for a curriculum."""
    CURRICULUM_CHOICES = [
        ('844', '8-4-4'),
        ('CBC', 'CBC'),
    ]
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='grade_scales')
    name = models.CharField(max_length=100)  # e.g., "KCSE Grading"
    curriculum = models.CharField(max_length=3, choices=CURRICULUM_CHOICES)
    grade = models.CharField(max_length=5)  # e.g., "A", "B+"
    min_mark = models.DecimalField(max_digits=5, decimal_places=2)
    max_mark = models.DecimalField(max_digits=5, decimal_places=2)
    points = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('school', 'curriculum', 'grade')
        ordering = ['-max_mark']

    def __str__(self):
        return f"{self.grade} ({self.min_mark} - {self.max_mark})"

class ExamType(BaseModel):
    """Type of exam (CAT, Mid-Term, etc.)."""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='exam_types')
    name = models.CharField(max_length=50)  # e.g., "CAT 1", "Mid-Term"
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)  # for final grade weighting
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('school', 'name')

    def __str__(self):
        return self.name

class Exam(BaseModel):
    """Defines a specific exam instance."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    ]
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='exams')
    exam_type = models.ForeignKey(ExamType, on_delete=models.PROTECT)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)
    term = models.ForeignKey(Term, on_delete=models.PROTECT)
    class_obj = models.ForeignKey(Class, on_delete=models.PROTECT, related_name='exams')
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    date = models.DateField()
    max_marks = models.DecimalField(max_digits=6, decimal_places=2)
    instructions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(Staff, on_delete=models.PROTECT, related_name='exams_created')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.exam_type.name} - {self.subject.name} ({self.academic_year.year})"

class ExamResult(BaseModel):
    """Marks obtained by a student for an exam."""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='exam_results')
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT, related_name='results')
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name='exam_results')
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    grade = models.CharField(max_length=5, blank=True)  # computed from GradeScale
    remarks = models.TextField(blank=True)
    teacher_comment = models.TextField(blank=True)
    principal_remark = models.TextField(blank=True)
    is_locked = models.BooleanField(default=False)  # prevent further edits

    class Meta:
        unique_together = ('exam', 'student')
        ordering = ['student']

    def __str__(self):
        return f"{self.student} - {self.exam}: {self.marks_obtained}"

    def save(self, *args, **kwargs):
        # Auto-calculate grade based on GradeScale for the school/curriculum
        if self.marks_obtained is not None:
            grade_scale = GradeScale.objects.filter(
                school=self.school,
                curriculum=self.exam.class_obj.curriculum,
                min_mark__lte=self.marks_obtained,
                max_mark__gte=self.marks_obtained
            ).first()
            if grade_scale:
                self.grade = grade_scale.grade
        super().save(*args, **kwargs)
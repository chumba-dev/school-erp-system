from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.models import BaseModel
from apps.schools.models import School
from apps.academics.models import Class, Stream, Subject, AcademicYear, Term
from apps.core.models import Staff

class SchoolDay(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='school_days')
    name = models.CharField(max_length=20)  # Monday, Tuesday, ...
    order = models.PositiveSmallIntegerField(unique=True)  # 1..7
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        unique_together = ('school', 'name')

    def __str__(self):
        return self.name

class Period(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='periods')
    name = models.CharField(max_length=50)  # Period 1, Break, Lunch, etc.
    start_time = models.TimeField()
    end_time = models.TimeField()
    order = models.PositiveSmallIntegerField()
    is_break = models.BooleanField(default=False)
    is_lunch = models.BooleanField(default=False)
    is_assembly = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']
        unique_together = ('school', 'order')

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"

class Room(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('school', 'name')

    def __str__(self):
        return self.name

class TeacherAvailability(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='teacher_availabilities')
    teacher = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='availabilities')
    day = models.ForeignKey(SchoolDay, on_delete=models.CASCADE)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('teacher', 'day', 'period')

    def __str__(self):
        return f"{self.teacher} - {self.day} {self.period}"

class SubjectAllocation(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='subject_allocations')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='subject_allocations')
    max_lessons_per_week = models.PositiveSmallIntegerField(default=5)
    max_lessons_per_day = models.PositiveSmallIntegerField(default=2)

    class Meta:
        unique_together = ('class_obj', 'stream', 'subject', 'teacher')
        ordering = ['class_obj', 'stream', 'subject']

    def __str__(self):
        stream_name = f" - {self.stream.name}" if self.stream else ""
        return f"{self.class_obj.name}{stream_name}: {self.subject} ({self.teacher})"

class Timetable(BaseModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='timetables')
    name = models.CharField(max_length=100)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)
    term = models.ForeignKey(Term, on_delete=models.PROTECT, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(Staff, on_delete=models.PROTECT, related_name='timetables_created')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class TimetableEntry(BaseModel):
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='entries')
    day = models.ForeignKey(SchoolDay, on_delete=models.CASCADE)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, null=True, blank=True)
    subject_allocation = models.ForeignKey(SubjectAllocation, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='timetable_entries')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            ('timetable', 'day', 'period', 'class_obj', 'stream'),  # class cannot have two subjects at same time
            ('timetable', 'day', 'period', 'teacher'),              # teacher cannot be double-booked
            ('timetable', 'day', 'period', 'room'),                 # room cannot be double-booked
        )
        ordering = ['day', 'period']

    def __str__(self):
        stream_name = f" - {self.stream.name}" if self.stream else ""
        return f"{self.class_obj.name}{stream_name}: {self.subject} ({self.teacher}) - {self.day} {self.period}"
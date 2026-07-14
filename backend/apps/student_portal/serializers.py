from rest_framework import serializers
from apps.core.models import Student
from apps.accounts.models import User
from apps.exams.models import ExamResult
from apps.timetable.models import TimetableEntry

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'admission_number', 'first_name', 'last_name', 'class_obj', 'stream', 'enrollment_status']

class ResultSerializer(serializers.ModelSerializer):
    exam_name = serializers.CharField(source='exam.exam_type.name')
    subject = serializers.CharField(source='exam.subject.name')
    term = serializers.CharField(source='exam.term.name')
    academic_year = serializers.IntegerField(source='exam.academic_year.year')

    class Meta:
        model = ExamResult
        fields = ['id', 'exam_name', 'subject', 'marks_obtained', 'grade', 'remarks', 'teacher_comment', 'is_locked', 'term', 'academic_year']

class TimetableEntrySerializer(serializers.ModelSerializer):
    day = serializers.CharField(source='day.name')
    period = serializers.CharField(source='period.name')
    subject = serializers.CharField(source='subject.name')
    teacher = serializers.CharField(source='teacher.first_name')
    room = serializers.CharField(source='room.name')

    class Meta:
        model = TimetableEntry
        fields = ['day', 'period', 'subject', 'teacher', 'room']
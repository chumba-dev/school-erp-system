from rest_framework import serializers
from apps.accounts.models import User
from apps.core.models import Student
from apps.finance.models import FeeInvoice, Payment
from apps.exams.models import ExamResult
from apps.timetable.models import TimetableEntry
from .models import ParentStudent

class ParentStudentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    admission_number = serializers.CharField(source='student.admission_number', read_only=True)

    class Meta:
        model = ParentStudent
        fields = ['id', 'student', 'student_name', 'admission_number', 'relationship', 'is_primary']

class ParentProfileSerializer(serializers.ModelSerializer):
    children = ParentStudentSerializer(source='children', many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'children']
        read_only_fields = ['id', 'username']
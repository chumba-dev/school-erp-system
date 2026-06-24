from rest_framework import serializers
from .models import Student, Staff, Department

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id', 'admission_number', 'first_name', 'last_name', 'middle_name',
            'parent_name', 'parent_phone', 'parent_email', 'class_obj', 'stream',
            'cbc_pathway', 'enrollment_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
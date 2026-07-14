from rest_framework import serializers
from .models import GradeScale, ExamType, Exam, ExamResult

class GradeScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeScale
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'school')

class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamType
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'school')

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'school', 'created_by')

class ExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamResult
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'school', 'grade')
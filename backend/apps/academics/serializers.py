from rest_framework import serializers
from .models import AcademicYear, Term, Class, Stream, Subject

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'school')

class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'school')

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'school')

class StreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'school')

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'school')
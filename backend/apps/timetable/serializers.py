from rest_framework import serializers
from .models import SchoolDay, Period, Room, TeacherAvailability, SubjectAllocation, Timetable, TimetableEntry

class SchoolDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolDay
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'school')

class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'school')

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'school')

class TeacherAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherAvailability
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'school')

class SubjectAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectAllocation
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'school')

class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'school', 'created_by')

class TimetableEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableEntry
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'school')
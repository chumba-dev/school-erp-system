from rest_framework import serializers
from .models import APIKey, LostBookEvent

class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'key', 'created_by', 'school')

class LostBookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = LostBookEvent
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'school')
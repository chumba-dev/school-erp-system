from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ('id', 'user', 'user_role', 'action', 'table_name',
                            'record_id', 'old_values', 'new_values',
                            'ip_address', 'created_at', 'updated_at', 'school')
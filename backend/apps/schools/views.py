from rest_framework import viewsets, permissions
from .models import School
from .serializers import SchoolSerializer
from apps.accounts.permissions import IsAdmin
import uuid
class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        # Generate subdomain from name if not provided
        subdomain = serializer.validated_data.get('subdomain')
        if not subdomain:
            name = serializer.validated_data.get('name')
            subdomain = name.lower().replace(' ', '')
            # Ensure uniqueness
            if School.objects.filter(subdomain=subdomain).exists():
                subdomain = f"{subdomain}-{uuid.uuid4().hex[:6]}"
        serializer.save(subdomain=subdomain, created_by=self.request.user.staff_profile)
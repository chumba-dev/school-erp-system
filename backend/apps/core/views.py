from rest_framework import viewsets, permissions

from apps.common.mixins import SchoolFilterMixin
from .models import Student, Staff, Department
from .serializers import StudentSerializer, StaffSerializer, DepartmentSerializer
from apps.accounts.permissions import IsAdmin, IsBursar

class DepartmentViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdmin | IsBursar]

class StaffViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAdmin | IsBursar]

class StudentViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdmin | IsBursar]
        return [permission() for permission in permission_classes]
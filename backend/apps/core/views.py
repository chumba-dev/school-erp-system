from requests import Response
from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

from apps.common.mixins import SchoolFilterMixin
from .models import Student, Staff, Department
from .serializers import StudentSerializer, StaffSerializer, DepartmentSerializer
from apps.accounts.permissions import IsAdmin, IsBursar, IsPrincipal

from apps.academics.models import AcademicYear, Class, Term
from apps.core.models import AcademicHistory

class DepartmentViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdmin | IsBursar | IsPrincipal]

class StaffViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAdmin | IsBursar | IsPrincipal]

class StudentViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdmin | IsBursar | IsPrincipal]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdmin | IsPrincipal])
    def promote(self, request):
        """
        Promote a batch of students to the next class.
        Expected payload: {
            "current_class_id": "<class_id>",
            "next_class_id": "<class_id>",
            "academic_year_id": "<year_id>",
            "term_id": "<term_id>",
            "students": ["student_id1", "student_id2", ...]  # optional; if not provided, all active students in the class are promoted.
        }
        """
        data = request.data
        current_class_id = data.get('current_class_id')
        next_class_id = data.get('next_class_id')
        year_id = data.get('academic_year_id')
        term_id = data.get('term_id')
        student_ids = data.get('students', [])

        if not all([current_class_id, next_class_id, year_id, term_id]):
            return Response({'error': 'current_class_id, next_class_id, academic_year_id, term_id required'}, status=400)

        current_class = get_object_or_404(Class, id=current_class_id, school=request.school)
        next_class = get_object_or_404(Class, id=next_class_id, school=request.school)
        year = get_object_or_404(AcademicYear, id=year_id, school=request.school)
        term = get_object_or_404(Term, id=term_id, academic_year=year, school=request.school)

        if student_ids:
            students = Student.objects.filter(id__in=student_ids, class_obj=current_class, school=request.school)
        else:
            students = Student.objects.filter(class_obj=current_class, school=request.school, academic_status='active')

        updated = []
        for student in students:
            # Record academic history
            AcademicHistory.objects.create(
                student=student,
                class_obj=current_class,
                academic_year=year,
                term=term,
                status='promoted',
                remarks=f"Promoted from {current_class.name} to {next_class.name}"
            )
            # Update student's class and status
            student.class_obj = next_class
            student.academic_status = 'promoted'
            student.save()
            updated.append(student.id)

        return Response({'status': 'success', 'promoted_students': updated})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin | IsPrincipal])
    def graduate(self, request, pk=None):
        student = self.get_object()
        if student.academic_status == 'graduated':
            return Response({'error': 'Student already graduated'}, status=400)
        # Record academic history
        current_year = AcademicYear.objects.filter(school=request.school, is_current=True).first()
        if not current_year:
            return Response({'error': 'No current academic year set'}, status=400)
        AcademicHistory.objects.create(
            student=student,
            class_obj=student.class_obj,
            academic_year=current_year,
            term=None,
            status='graduated',
            remarks=request.data.get('remarks', '')
        )
        student.academic_status = 'graduated'
        student.save()
        return Response({'status': 'graduated'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin | IsPrincipal])
    def repeat(self, request, pk=None):
        student = self.get_object()
        if student.academic_status == 'repeated':
            return Response({'error': 'Student already repeated'}, status=400)
        current_year = AcademicYear.objects.filter(school=request.school, is_current=True).first()
        if not current_year:
            return Response({'error': 'No current academic year set'}, status=400)
        AcademicHistory.objects.create(
            student=student,
            class_obj=student.class_obj,
            academic_year=current_year,
            term=None,
            status='repeated',
            remarks=request.data.get('remarks', '')
        )
        student.academic_status = 'repeated'
        student.save()
        return Response({'status': 'repeated'})
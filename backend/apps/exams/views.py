from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Min, Sum, Avg, Max
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from apps.common.mixins import SchoolFilterMixin
from apps.accounts.permissions import IsAdmin, IsBursar, IsPrincipal, IsTeacher, IsParent
from apps.core.models import Student
from apps.academics.models import Term, Class
from .models import GradeScale, ExamType, Exam, ExamResult
from .serializers import (
    GradeScaleSerializer, ExamTypeSerializer, ExamSerializer, ExamResultSerializer
)
from .report_utils import generate_report_card

# ---------- GradeScale ViewSet ----------
class GradeScaleViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = GradeScale.objects.all()
    serializer_class = GradeScaleSerializer
    permission_classes = [IsAdmin | IsPrincipal | IsTeacher]

# ---------- ExamType ViewSet ----------
class ExamTypeViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = ExamType.objects.all()
    serializer_class = ExamTypeSerializer
    permission_classes = [IsAdmin | IsPrincipal | IsTeacher]

# ---------- Exam ViewSet ----------
class ExamViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAdmin | IsPrincipal | IsTeacher]

    def perform_create(self, serializer):
        # Call super to set school (from mixin)
        super().perform_create(serializer)
        # Then set created_by manually
        serializer.save(created_by=self.request.user.staff_profile)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'teacher':
            taught_subjects = user.staff_profile.subjects_taught.values_list('subject_id', flat=True)
            qs = qs.filter(subject_id__in=taught_subjects)
        return qs
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin | IsPrincipal])
    def publish(self, request, pk=None):
        exam = self.get_object()
        if exam.status == 'published':
            return Response({'error': 'Exam already published'}, status=400)
        exam.status = 'published'
        exam.save()
        return Response({'status': 'published'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin | IsPrincipal])
    def close(self, request, pk=None):
        exam = self.get_object()
        if exam.status == 'closed':
            return Response({'error': 'Exam already closed'}, status=400)
        exam.status = 'closed'
        exam.save()
        return Response({'status': 'closed'})

# ---------- ExamResult ViewSet ----------
class ExamResultViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = ExamResult.objects.all()
    serializer_class = ExamResultSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin | IsPrincipal | IsTeacher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'teacher':
            taught_subjects = user.staff_profile.subjects_taught.values_list('subject_id', flat=True)
            qs = qs.filter(exam__subject_id__in=taught_subjects)
        elif user.role in ['parent', 'student']:
            qs = qs.filter(exam__status='published')
            if user.student_profile:
                qs = qs.filter(student=user.student_profile)
            else:
                qs = qs.none()
        return qs

    def perform_create(self, serializer):
        # Call super to set school
        super().perform_create(serializer)
        # Teacher permission check
        user = self.request.user
        if user.role not in ['admin', 'principal']:
            exam = serializer.validated_data.get('exam')
            if not user.staff_profile.subjects_taught.filter(subject=exam.subject).exists():
                raise PermissionDenied("You are not allowed to enter marks for this subject.")
        # The serializer.save() is already done by super; no need to call again.

    @action(detail=False, methods=['post'], permission_classes=[IsAdmin | IsPrincipal | IsTeacher])
    def bulk_upload(self, request):
        data = request.data
        exam_id = data.get('exam_id')
        results_data = data.get('results', [])
        if not exam_id or not results_data:
            return Response({'error': 'exam_id and results list required'}, status=400)
        exam = Exam.objects.get(id=exam_id)
        user = request.user
        if user.role not in ['admin', 'principal']:
            if not user.staff_profile.subjects_taught.filter(subject=exam.subject).exists():
                return Response({'error': 'Not allowed'}, status=403)
        created = []
        for item in results_data:
            student_id = item.get('student_id')
            marks = item.get('marks_obtained')
            if not student_id or marks is None:
                continue
            # Use update_or_create to avoid duplicates; school will be set by mixin? We'll set manually.
            result, _ = ExamResult.objects.update_or_create(
                exam=exam,
                student_id=student_id,
                defaults={
                    'marks_obtained': marks,
                    'school': request.school
                }
            )
            created.append(result.id)
        return Response({'status': 'success', 'created': created})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin | IsPrincipal])
    def lock(self, request, pk=None):
        result = self.get_object()
        result.is_locked = True
        result.save()
        return Response({'status': 'locked'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin | IsPrincipal])
    def unlock(self, request, pk=None):
        result = self.get_object()
        result.is_locked = False
        result.save()
        return Response({'status': 'unlocked'})

    @action(detail=False, methods=['get'], url_path='report-card')
    def report_card(self, request):
        student_id = request.query_params.get('student_id')
        term_id = request.query_params.get('term_id')
        if not student_id or not term_id:
            return Response({'error': 'student_id and term_id required'}, status=400)

        student = get_object_or_404(Student, id=student_id, school=request.school)
        term = get_object_or_404(Term, id=term_id, academic_year__school=request.school)

        results = ExamResult.objects.filter(
            student=student,
            exam__term=term,
            exam__academic_year=term.academic_year
        ).select_related('exam__subject')

        if not results.exists():
            return Response({'error': 'No results found for this student in the given term'}, status=404)

        pdf_bytes = generate_report_card(student, results, term, term.academic_year)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="report_card_{student.admission_number}_{term.name}.pdf"'
        return response

    @action(detail=False, methods=['get'], url_path='ranking')
    def ranking(self, request):
        exam_id = request.query_params.get('exam_id')
        class_id = request.query_params.get('class_id')
        term_id = request.query_params.get('term_id')

        if exam_id:
            exam = get_object_or_404(Exam, id=exam_id, school=request.school)
            results = ExamResult.objects.filter(exam=exam).select_related('student')
            ranked = results.order_by('-marks_obtained')
            data = []
            for idx, r in enumerate(ranked, start=1):
                data.append({
                    'rank': idx,
                    'student': r.student.id,
                    'student_name': f"{r.student.first_name} {r.student.last_name}",
                    'marks': r.marks_obtained,
                    'grade': r.grade,
                })
            return Response(data)

        elif class_id and term_id:
            class_obj = get_object_or_404(Class, id=class_id, school=request.school)
            term = get_object_or_404(Term, id=term_id, academic_year__school=request.school)
            students = Student.objects.filter(class_obj=class_obj, school=request.school)
            rankings = []
            for student in students:
                results = ExamResult.objects.filter(
                    student=student,
                    exam__term=term,
                    exam__academic_year=term.academic_year
                )
                if results.exists():
                    total = results.aggregate(total=Sum('marks_obtained'))['total'] or 0
                    count = results.count()
                    mean = total / count if count > 0 else 0
                    rankings.append({
                        'student': student.id,
                        'student_name': f"{student.first_name} {student.last_name}",
                        'mean': mean,
                    })
            rankings.sort(key=lambda x: x['mean'], reverse=True)
            for idx, item in enumerate(rankings, start=1):
                item['rank'] = idx
            return Response(rankings)
        else:
            return Response({'error': 'Provide either exam_id or (class_id + term_id)'}, status=400)

    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        exam_id = request.query_params.get('exam_id')
        if not exam_id:
            return Response({'error': 'exam_id required'}, status=400)
        exam = get_object_or_404(Exam, id=exam_id, school=request.school)
        results = ExamResult.objects.filter(exam=exam)
        count = results.count()
        if count == 0:
            return Response({'error': 'No results for this exam'}, status=404)
        total = results.aggregate(total=Sum('marks_obtained'))['total'] or 0
        avg = total / count
        max_mark = results.aggregate(max=Max('marks_obtained'))['max'] or 0
        min_mark = results.aggregate(min=Min('marks_obtained'))['min'] or 0
        pass_threshold = exam.max_marks * 0.5
        passed = results.filter(marks_obtained__gte=pass_threshold).count()
        pass_rate = (passed / count) * 100 if count > 0 else 0
        return Response({
            'exam': exam.id,
            'total_students': count,
            'average_mark': avg,
            'highest_mark': max_mark,
            'lowest_mark': min_mark,
            'pass_rate': pass_rate,
        })
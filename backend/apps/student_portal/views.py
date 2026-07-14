from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.accounts.permissions import IsStudent
from apps.core.models import Student
from apps.exams.models import ExamResult
from apps.timetable.models import TimetableEntry
from .serializers import StudentProfileSerializer, ResultSerializer, TimetableEntrySerializer

# ---------- Profile ----------
class StudentProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsStudent]

    def get_object(self):
        return self.request.user.student_profile

# ---------- Results ----------
class StudentResultsView(generics.ListAPIView):
    serializer_class = ResultSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        student = self.request.user.student_profile
        return ExamResult.objects.filter(student=student).select_related('exam__exam_type', 'exam__subject', 'exam__term', 'exam__academic_year')

# ---------- Report Card ----------
class StudentReportCardView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        # For now, we redirect to the existing report card endpoint or implement a simple stub.
        # In real implementation, you can use the existing report card generation.
        student = request.user.student_profile
        # Return a placeholder or call the exam report card generator.
        return Response({'message': 'Report card generation coming soon'}, status=200)

# ---------- Timetable ----------
class StudentTimetableView(generics.ListAPIView):
    serializer_class = TimetableEntrySerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        student = self.request.user.student_profile
        # Filter by class and stream
        qs = TimetableEntry.objects.filter(class_obj=student.class_obj)
        if student.stream:
            qs = qs.filter(stream=student.stream)
        return qs

# ---------- Assignments (stub) ----------
class StudentAssignmentsView(generics.ListAPIView):
    permission_classes = [IsStudent]

    def get(self, request):
        return Response({'message': 'Assignments will be available once LMS is integrated'}, status=200)

# ---------- Learning Materials (stub) ----------
class StudentMaterialsView(generics.ListAPIView):
    permission_classes = [IsStudent]

    def get(self, request):
        return Response({'message': 'Learning materials will be available once LMS is integrated'}, status=200)

# ---------- Attendance (stub) ----------
class StudentAttendanceView(generics.ListAPIView):
    permission_classes = [IsStudent]

    def get(self, request):
        return Response({'message': 'Attendance tracking will be available once implemented'}, status=200)

# ---------- Notifications (stub) ----------
class StudentNotificationsView(generics.ListAPIView):
    permission_classes = [IsStudent]

    def get(self, request):
        return Response({'message': 'Notifications will be available once implemented'}, status=200)

class StudentNotificationReadView(APIView):
    permission_classes = [IsStudent]

    def patch(self, request, pk):
        return Response({'message': 'Notifications will be available once implemented'}, status=200)
from django.urls import path
from .views import (
    StudentProfileView, StudentResultsView, StudentReportCardView,
    StudentTimetableView, StudentAssignmentsView, StudentMaterialsView,
    StudentAttendanceView, StudentNotificationsView, StudentNotificationReadView
)

urlpatterns = [
    path('profile/', StudentProfileView.as_view(), name='student-profile'),
    path('results/', StudentResultsView.as_view(), name='student-results'),
    path('report-card/', StudentReportCardView.as_view(), name='student-report-card'),
    path('timetable/', StudentTimetableView.as_view(), name='student-timetable'),
    path('assignments/', StudentAssignmentsView.as_view(), name='student-assignments'),
    path('materials/', StudentMaterialsView.as_view(), name='student-materials'),
    path('attendance/', StudentAttendanceView.as_view(), name='student-attendance'),
    path('notifications/', StudentNotificationsView.as_view(), name='student-notifications'),
    path('notifications/<int:pk>/read/', StudentNotificationReadView.as_view(), name='student-notification-read'),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SchoolDayViewSet, PeriodViewSet, RoomViewSet,
    TeacherAvailabilityViewSet, SubjectAllocationViewSet,
    TimetableViewSet, TimetableEntryViewSet
)

router = DefaultRouter()
router.register(r'school-days', SchoolDayViewSet)
router.register(r'periods', PeriodViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'teacher-availability', TeacherAvailabilityViewSet)
router.register(r'subject-allocations', SubjectAllocationViewSet)
router.register(r'timetables', TimetableViewSet)
router.register(r'timetable-entries', TimetableEntryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
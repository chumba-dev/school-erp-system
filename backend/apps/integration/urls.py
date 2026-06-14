from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    APIKeyViewSet, LostBookEventViewSet,
    lost_book_event, student_clearance_status, webhook_receiver,
    sync_students, sync_staff, test_connection
)

router = DefaultRouter()
router.register(r'api-keys', APIKeyViewSet)
router.register(r'lost-book-events', LostBookEventViewSet)   # new

urlpatterns = [
    path('', include(router.urls)),
    path('lms/lost-book/', lost_book_event, name='lost-book-event'),
    path('lms/clearance/<str:admission_number>/', student_clearance_status, name='clearance-status'),
    path('lms/sync/students/', sync_students, name='sync-students'),
    path('lms/sync/staff/', sync_staff, name='sync-staff'),
    path('lms/test-connection/', test_connection, name='test-connection'),
    path('webhook/<str:webhook_name>/', webhook_receiver, name='webhook'),
]
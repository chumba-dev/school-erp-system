from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, StaffViewSet, DepartmentViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'staff', StaffViewSet)
router.register(r'departments', DepartmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
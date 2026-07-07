from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GradeScaleViewSet, ExamTypeViewSet, ExamViewSet, ExamResultViewSet

router = DefaultRouter()
router.register(r'grade-scales', GradeScaleViewSet)
router.register(r'exam-types', ExamTypeViewSet)
router.register(r'exams', ExamViewSet)
router.register(r'results', ExamResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
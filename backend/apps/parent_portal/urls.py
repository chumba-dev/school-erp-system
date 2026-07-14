from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParentPortalViewSet

router = DefaultRouter()
router.register(r'', ParentPortalViewSet, basename='parent')

urlpatterns = [
    path('', include(router.urls)),
]
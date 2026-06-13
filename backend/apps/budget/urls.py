from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BudgetPeriodViewSet, BudgetCategoryViewSet, BudgetLineItemViewSet

router = DefaultRouter()
router.register(r'periods', BudgetPeriodViewSet)
router.register(r'categories', BudgetCategoryViewSet)
router.register(r'line-items', BudgetLineItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
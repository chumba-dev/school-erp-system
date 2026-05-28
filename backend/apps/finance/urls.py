from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FeeInvoiceViewSet, PaymentViewSet, ExpenseCategoryViewSet, ExpenseViewSet
)

router = DefaultRouter()
router.register(r'invoices', FeeInvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'expense-categories', ExpenseCategoryViewSet, basename='expense-category')
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    path('', include(router.urls)),
]
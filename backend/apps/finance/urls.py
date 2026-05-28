from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FeeInvoiceViewSet, PaymentViewSet, ExpenseCategoryViewSet, ExpenseViewSet, ReconciliationLogViewSet, StudentCreditViewSet
)

router = DefaultRouter()
router.register(r'invoices', FeeInvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'expense-categories', ExpenseCategoryViewSet, basename='expense-category')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'reconciliation-logs', ReconciliationLogViewSet, basename='reconciliation-log')
router.register(r'student-credits', StudentCreditViewSet, basename='student-credit')

urlpatterns = [
    path('', include(router.urls)),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FeeInvoiceViewSet, PaymentViewSet, ExpenseCategoryViewSet, ExpenseViewSet,
    ReconciliationLogViewSet, StudentCreditViewSet, PaymentReceiptView
)

router = DefaultRouter()
router.register(r'invoices', FeeInvoiceViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'expense-categories', ExpenseCategoryViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'reconciliation-logs', ReconciliationLogViewSet)
router.register(r'student-credits', StudentCreditViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('payments/<uuid:payment_id>/receipt/', PaymentReceiptView.as_view(), name='payment_receipt'),
]
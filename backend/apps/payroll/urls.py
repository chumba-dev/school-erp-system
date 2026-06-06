from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SalaryStructureViewSet, PayrollDeductionSettingViewSet, PayrollRunViewSet,
    PayrollEntryViewSet, PayrollPaymentLogViewSet, PayrollEntryPayslipView  
)

router = DefaultRouter()
router.register(r'salary-structures', SalaryStructureViewSet)
router.register(r'deduction-settings', PayrollDeductionSettingViewSet)
router.register(r'runs', PayrollRunViewSet)
router.register(r'entries', PayrollEntryViewSet)
router.register(r'payment-logs', PayrollPaymentLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('entries/<uuid:entry_id>/payslip/', PayrollEntryPayslipView.as_view(), name='payslip'),
]
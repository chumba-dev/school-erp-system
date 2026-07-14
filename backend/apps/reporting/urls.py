from django.urls import path
from .views import (
    FeeCollectionReportView, OutstandingBalancesReportView, InvoiceReportView,
    ExpenseReportView, RevenueVsExpenditureReportView, MonthlyPayrollSummaryView,
    PayrollByDepartmentView, StatutoryDeductionsReportView, BudgetSummaryReportView,
    StudentBalancesView, StudentsWithArrearsView
)

urlpatterns = [
    path('fee-collection/', FeeCollectionReportView.as_view(), name='fee-collection'),
    path('outstanding-balances/', OutstandingBalancesReportView.as_view(), name='outstanding-balances'),
    path('invoices/', InvoiceReportView.as_view(), name='invoices'),
    path('expenses/', ExpenseReportView.as_view(), name='expenses'),
    path('revenue-expenditure/', RevenueVsExpenditureReportView.as_view(), name='rev-exp'),
    path('payroll/monthly/', MonthlyPayrollSummaryView.as_view(), name='payroll-monthly'),
    path('payroll/department/', PayrollByDepartmentView.as_view(), name='payroll-dept'),
    path('payroll/statutory/', StatutoryDeductionsReportView.as_view(), name='payroll-statutory'),
    path('budget/summary/', BudgetSummaryReportView.as_view(), name='budget-summary'),
    path('student/balances/', StudentBalancesView.as_view(), name='student-balances'),
    path('student/arrears/', StudentsWithArrearsView.as_view(), name='student-arrears'),
]
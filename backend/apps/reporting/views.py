from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.http import HttpResponse
from decimal import Decimal
import csv
from openpyxl import Workbook
from apps.accounts.permissions import IsBursar, IsAdmin
from apps.finance.models import Payment, FeeInvoice, Expense
from apps.payroll.models import PayrollEntry, PayrollRun
from apps.budget.models import BudgetLineItem, BudgetPeriod
from apps.core.models import Student, Staff
from .utils import generate_pdf_report, generate_excel_report, generate_csv_report


# ---------- Helper to format decimal ----------
def fmt_decimal(d):
    return str(d) if d is not None else '0.00'

# ---------- 1. Fee Collection Report ----------
class FeeCollectionReportView(APIView):
    permission_classes = [IsBursar | IsAdmin]

    def get(self, request):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        #format_type = request.query_params.get('format', 'json')
        export_type = request.query_params.get('export', 'json')

        qs = Payment.objects.filter(status='completed')
        if date_from:
            qs = qs.filter(payment_date__date__gte=date_from)
        if date_to:
            qs = qs.filter(payment_date__date__lte=date_to)

        total_collected = qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        payment_count = qs.count()

        data = []
        for p in qs.select_related('student', 'invoice'):
            data.append([
                p.payment_date.strftime('%Y-%m-%d %H:%M:%S'),
                p.student.admission_number,
                f"{p.student.first_name} {p.student.last_name}",
                p.transaction_reference,
                fmt_decimal(p.amount),
                p.get_payment_method_display(),
            ])
        headers = ['Date', 'Admission No', 'Student Name', 'Transaction Ref', 'Amount (KES)', 'Method']

        if export_type == 'pdf':
            return generate_pdf_report('Fee Collection Report', headers, data, 'fee_collection.pdf')
        elif export_type == 'excel':
            return generate_excel_report('Fee Collection', headers, data, 'fee_collection.xlsx')
        elif export_type == 'csv':
            return generate_csv_report(headers, data, 'fee_collection.csv')
        else:
            return Response({
                'total_collected': fmt_decimal(total_collected),
                'payment_count': payment_count,
                'payments': data
            })

# ---------- 2. Outstanding Balances Report ----------
class OutstandingBalancesReportView(APIView):
    permission_classes = [IsBursar | IsAdmin]

    def get(self, request):
        export_type = request.query_params.get('export', 'json')
        students = Student.objects.filter(enrollment_status='Active')
        data = []
        for s in students:
            total_invoiced = FeeInvoice.objects.filter(student=s).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            total_paid = Payment.objects.filter(student=s, status='completed').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            balance = total_invoiced - total_paid
            if balance > 0:
                data.append([
                    s.admission_number,
                    f"{s.first_name} {s.last_name}",
                    fmt_decimal(balance)
                ])
        headers = ['Admission No', 'Student Name', 'Outstanding Balance (KES)']

        if export_type == 'pdf':
            return generate_pdf_report('Outstanding Balances', headers, data, 'outstanding.pdf')
        elif export_type == 'excel':
            return generate_excel_report('Outstanding Balances', headers, data, 'outstanding.xlsx')
        elif export_type == 'csv':
            return generate_csv_report(headers, data, 'outstanding.csv')
        else:
            return Response(data)

# ---------- 3. Invoice Report ----------
class InvoiceReportView(APIView):
    permission_classes = [IsBursar | IsAdmin]

    def get(self, request):
        status_filter = request.query_params.get('status')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        export_type = request.query_params.get('export', 'json')

        qs = FeeInvoice.objects.all()
        if status_filter:
            qs = qs.filter(status=status_filter)
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        data = []
        for inv in qs.select_related('student', 'academic_year', 'term'):
            data.append([
                inv.invoice_number,
                inv.student.admission_number,
                f"{inv.student.first_name} {inv.student.last_name}",
                fmt_decimal(inv.total_amount),
                fmt_decimal(inv.paid_amount),
                fmt_decimal(inv.balance_due),
                inv.status,
                inv.due_date.strftime('%Y-%m-%d')
            ])
        headers = ['Invoice No', 'Admission No', 'Student Name', 'Total (KES)', 'Paid (KES)', 'Balance (KES)', 'Status', 'Due Date']

        if export_type == 'pdf':
            return generate_pdf_report('Invoice Report', headers, data, 'invoices.pdf')
        elif export_type == 'excel':
            return generate_excel_report('Invoices', headers, data, 'invoices.xlsx')
        elif export_type == 'csv':
            return generate_csv_report(headers, data, 'invoices.csv')
        else:
            return Response(data)

# ---------- 4. Expense Report ----------
class ExpenseReportView(APIView):
    permission_classes = [IsBursar | IsAdmin]

    def get(self, request):
        category = request.query_params.get('category')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        export_type = request.query_params.get('export', 'json')

        qs = Expense.objects.filter(status='paid')
        if category:
            qs = qs.filter(category_id=category)
        if date_from:
            qs = qs.filter(expense_date__gte=date_from)
        if date_to:
            qs = qs.filter(expense_date__lte=date_to)

        data = []
        for exp in qs.select_related('category'):
            data.append([
                exp.expense_number,
                exp.title,
                exp.category.name if exp.category else '-',
                fmt_decimal(exp.amount),
                exp.expense_date.strftime('%Y-%m-%d'),
                exp.payee_name,
                exp.status
            ])
        headers = ['Expense No', 'Title', 'Category', 'Amount (KES)', 'Date', 'Payee', 'Status']
        total = sum(Decimal(d[3]) for d in data)

        if export_type == 'pdf':
            return generate_pdf_report('Expense Report', headers, data, 'expenses.pdf')
        elif export_type == 'excel':
            return generate_excel_report('Expenses', headers, data, 'expenses.xlsx')
        elif export_type == 'csv':
            return generate_csv_report(headers, data, 'expenses.csv')
        else:
            return Response({'total_expenses': fmt_decimal(total), 'expenses': data})

# ---------- 5. Revenue vs Expenditure Report ----------
class RevenueVsExpenditureReportView(APIView):
    permission_classes = [IsBursar | IsAdmin]

    def get(self, request):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        export_type = request.query_params.get('export', 'json')

        # Revenue from payments
        rev_qs = Payment.objects.filter(status='completed')
        if date_from:
            rev_qs = rev_qs.filter(payment_date__date__gte=date_from)
        if date_to:
            rev_qs = rev_qs.filter(payment_date__date__lte=date_to)
        revenue = rev_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Expenditure from expenses (paid) + payroll (completed runs)
        exp_qs = Expense.objects.filter(status='paid')
        if date_from:
            exp_qs = exp_qs.filter(expense_date__gte=date_from)
        if date_to:
            exp_qs = exp_qs.filter(expense_date__lte=date_to)
        expense_total = exp_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        payroll_qs = PayrollEntry.objects.filter(payment_status='completed', payroll_run__paid_at__isnull=False)
        if date_from:
            payroll_qs = payroll_qs.filter(payroll_run__paid_at__date__gte=date_from)
        if date_to:
            payroll_qs = payroll_qs.filter(payroll_run__paid_at__date__lte=date_to)
        payroll_total = payroll_qs.aggregate(total=Sum('net_pay'))['total'] or Decimal('0.00')

        expenditure = expense_total + payroll_total
        net = revenue - expenditure

        if export_type == 'pdf':
            data = [
                ['Revenue', fmt_decimal(revenue)],
                ['Expenditure', fmt_decimal(expenditure)],
                ['Net Surplus/Deficit', fmt_decimal(net)]
            ]
            return generate_pdf_report('Revenue vs Expenditure', ['Category', 'Amount (KES)'], data, 'rev_exp.pdf')
        elif export_type == 'excel':
            wb = Workbook()
            ws = wb.active
            ws.title = 'Revenue vs Expenditure'
            ws.append(['Category', 'Amount (KES)'])
            ws.append(['Revenue', revenue])
            ws.append(['Expenditure', expenditure])
            ws.append(['Net', net])
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="rev_exp.xlsx"'
            wb.save(response)
            return response
        elif export_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="rev_exp.csv"'
            writer = csv.writer(response)
            writer.writerow(['Category', 'Amount (KES)'])
            writer.writerow(['Revenue', revenue])
            writer.writerow(['Expenditure', expenditure])
            writer.writerow(['Net', net])
            return response
        else:
            return Response({
                'revenue': fmt_decimal(revenue),
                'expenditure': fmt_decimal(expenditure),
                'net': fmt_decimal(net)
            })

# ---------- 6. Monthly Payroll Summary ----------
class MonthlyPayrollSummaryView(APIView):
    permission_classes = [IsBursar | IsAdmin]

    def get(self, request):
        year = request.query_params.get('year')
        export_type = request.query_params.get('export', 'json')
        qs = PayrollRun.objects.filter(status='paid')
        if year:
            qs = qs.filter(academic_year__year=year)
        data = []
        for run in qs.order_by('-academic_year__year', '-month'):
            data.append([
                f"{run.academic_year.year} - Month {run.month}",
                fmt_decimal(run.total_gross),
                fmt_decimal(run.total_deductions),
                fmt_decimal(run.total_net)
            ])
        headers = ['Period', 'Gross Pay (KES)', 'Total Deductions (KES)', 'Net Pay (KES)']

        if export_type == 'pdf':
            return generate_pdf_report('Monthly Payroll Summary', headers, data, 'payroll_monthly.pdf')
        elif export_type == 'excel':
            return generate_excel_report('Payroll Summary', headers, data, 'payroll_monthly.xlsx')
        elif export_type == 'csv':
            return generate_csv_report(headers, data, 'payroll_monthly.csv')
        else:
            return Response(data)

# ---------- 7. Payroll by Department ----------
class PayrollByDepartmentView(APIView):
    permission_classes = [IsBursar | IsAdmin]

    def get(self, request):
        year = request.query_params.get('year')
        export_type = request.query_params.get('export', 'json')
        qs = PayrollEntry.objects.filter(payment_status='completed')
        if year:
            qs = qs.filter(payroll_run__academic_year__year=year)
        dept_totals = {}
        for entry in qs.select_related('staff__department'):
            dept = entry.staff.department.name if entry.staff.department else 'No Department'
            dept_totals[dept] = dept_totals.get(dept, Decimal('0.00')) + entry.net_pay
        data = [[dept, fmt_decimal(total)] for dept, total in dept_totals.items()]
        headers = ['Department', 'Total Net Pay (KES)']

        if export_type == 'pdf':
            return generate_pdf_report('Payroll by Department', headers, data, 'payroll_dept.pdf')
        elif export_type == 'excel':
            return generate_excel_report('Payroll by Dept', headers, data, 'payroll_dept.xlsx')
        elif export_type == 'csv':
            return generate_csv_report(headers, data, 'payroll_dept.csv')
        else:
            return Response(data)

# ---------- 8. Statutory Deductions Report ----------
class StatutoryDeductionsReportView(APIView):
    permission_classes = [IsBursar | IsAdmin]

    def get(self, request):
        year = request.query_params.get('year')
        export_type = request.query_params.get('export', 'json')
        qs = PayrollEntry.objects.filter(payment_status='completed')
        if year:
            qs = qs.filter(payroll_run__academic_year__year=year)
        totals = qs.aggregate(
            paye=Sum('paye_tax'),
            nhif=Sum('nhif_deduction'),
            nssf=Sum('nssf_deduction'),
            shif=Sum('shaf_deduction'),
            housing=Sum('housing_levy')
        )
        data = [
            ['PAYE', fmt_decimal(totals['paye'])],
            ['NHIF', fmt_decimal(totals['nhif'])],
            ['NSSF', fmt_decimal(totals['nssf'])],
            ['SHIF (SHA)', fmt_decimal(totals['shif'])],
            ['Housing Levy', fmt_decimal(totals['housing'])],
        ]
        headers = ['Deduction Type', 'Total (KES)']

        if export_type == 'pdf':
            return generate_pdf_report('Statutory Deductions', headers, data, 'statutory.pdf')
        elif export_type == 'excel':
            return generate_excel_report('Statutory Deductions', headers, data, 'statutory.xlsx')
        elif export_type == 'csv':
            return generate_csv_report(headers, data, 'statutory.csv')
        else:
            return Response(data)

# ---------- 9. Budget Summary Report ----------
class BudgetSummaryReportView(APIView):
    permission_classes = [IsBursar | IsAdmin]

    def get(self, request):
        period_id = request.query_params.get('budget_period')
        export_type = request.query_params.get('export', 'json')
        qs = BudgetLineItem.objects.all()
        if period_id:
            qs = qs.filter(budget_period_id=period_id)
        rev_planned = qs.filter(category__type='revenue').aggregate(total=Sum('planned_amount'))['total'] or Decimal('0.00')
        rev_actual = qs.filter(category__type='revenue').aggregate(total=Sum('actual_amount'))['total'] or Decimal('0.00')
        exp_planned = qs.filter(category__type='expenditure').aggregate(total=Sum('planned_amount'))['total'] or Decimal('0.00')
        exp_actual = qs.filter(category__type='expenditure').aggregate(total=Sum('actual_amount'))['total'] or Decimal('0.00')
        data = [
            ['Revenue', fmt_decimal(rev_planned), fmt_decimal(rev_actual), fmt_decimal(rev_actual - rev_planned)],
            ['Expenditure', fmt_decimal(exp_planned), fmt_decimal(exp_actual), fmt_decimal(exp_actual - exp_planned)],
            ['Net', fmt_decimal(rev_planned - exp_planned), fmt_decimal(rev_actual - exp_actual), fmt_decimal((rev_actual - exp_actual) - (rev_planned - exp_planned))]
        ]
        headers = ['Category', 'Planned (KES)', 'Actual (KES)', 'Variance (KES)']

        if export_type == 'pdf':
            return generate_pdf_report('Budget Summary', headers, data, 'budget_summary.pdf')
        elif export_type == 'excel':
            return generate_excel_report('Budget Summary', headers, data, 'budget_summary.xlsx')
        elif export_type == 'csv':
            return generate_csv_report(headers, data, 'budget_summary.csv')
        else:
            return Response(data)

# ---------- 10. Student Balances (All) ----------
class StudentBalancesView(APIView):
    permission_classes = [IsBursar | IsAdmin]

    def get(self, request):
        export_type = request.query_params.get('export', 'json')
        students = Student.objects.filter(enrollment_status='Active')
        data = []
        for s in students:
            total_invoiced = FeeInvoice.objects.filter(student=s).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            total_paid = Payment.objects.filter(student=s, status='completed').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            balance = total_invoiced - total_paid
            data.append([
                s.admission_number,
                f"{s.first_name} {s.last_name}",
                fmt_decimal(balance)
            ])
        headers = ['Admission No', 'Student Name', 'Balance (KES)']

        if export_type == 'pdf':
            return generate_pdf_report('All Student Balances', headers, data, 'student_balances.pdf')
        elif export_type == 'excel':
            return generate_excel_report('Student Balances', headers, data, 'student_balances.xlsx')
        elif export_type == 'csv':
            return generate_csv_report(headers, data, 'student_balances.csv')
        else:
            return Response(data)

# ---------- 11. Students with Arrears (Only those with balance > 0) ----------
class StudentsWithArrearsView(APIView):
    permission_classes = [IsBursar | IsAdmin]

    def get(self, request):
        export_type = request.query_params.get('export', 'json')
        students = Student.objects.filter(enrollment_status='Active')
        data = []
        for s in students:
            total_invoiced = FeeInvoice.objects.filter(student=s).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            total_paid = Payment.objects.filter(student=s, status='completed').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            balance = total_invoiced - total_paid
            if balance > 0:
                data.append([
                    s.admission_number,
                    f"{s.first_name} {s.last_name}",
                    fmt_decimal(balance)
                ])
        headers = ['Admission No', 'Student Name', 'Arrears (KES)']

        if export_type == 'pdf':
            return generate_pdf_report('Students with Arrears', headers, data, 'arrears.pdf')
        elif export_type == 'excel':
            return generate_excel_report('Arrears', headers, data, 'arrears.xlsx')
        elif export_type == 'csv':
            return generate_csv_report(headers, data, 'arrears.csv')
        else:
            return Response(data)
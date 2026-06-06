from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from .models import (
    SalaryStructure, PayrollDeductionSetting, PayrollRun, PayrollEntry, PayrollPaymentLog
)
from .serializers import (
    SalaryStructureSerializer, PayrollDeductionSettingSerializer,
    PayrollRunSerializer, PayrollEntrySerializer, PayrollPaymentLogSerializer
)
from .utils import calculate_paye, calculate_nhif, calculate_nssf, calculate_shif, calculate_housing_levy
from apps.accounts.permissions import IsBursar, IsAdmin
from apps.core.models import Staff

from rest_framework.views import APIView
from django.http import HttpResponse
from .payslip_utils import generate_payslip_pdf

from rest_framework.permissions import IsAuthenticated
from apps.accounts.permissions import IsTeacher

from django.shortcuts import get_object_or_404

class SalaryStructureViewSet(viewsets.ModelViewSet):
    queryset = SalaryStructure.objects.all()
    serializer_class = SalaryStructureSerializer
    permission_classes = [IsBursar | IsAdmin]

class PayrollDeductionSettingViewSet(viewsets.ModelViewSet):
    queryset = PayrollDeductionSetting.objects.all()
    serializer_class = PayrollDeductionSettingSerializer
    permission_classes = [IsBursar | IsAdmin]

class PayrollRunViewSet(viewsets.ModelViewSet):
    queryset = PayrollRun.objects.all()
    serializer_class = PayrollRunSerializer
    permission_classes = [IsBursar | IsAdmin]

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def process(self, request, pk=None):
        payroll_run = self.get_object()
        if payroll_run.status != 'draft':
            return Response({'error': 'Only draft runs can be processed'}, status=status.HTTP_400_BAD_REQUEST)

        # Get deduction settings for the run's year
        try:
            settings = PayrollDeductionSetting.objects.get(effective_year=payroll_run.academic_year.year)
        except PayrollDeductionSetting.DoesNotExist:
            return Response({'error': f'Deduction settings for year {payroll_run.academic_year.year} not found'}, status=400)

        # Get all active staff with a salary structure effective during this run
        # We'll consider the run's month/year; we need the salary structure effective from <= run date and effective_to >= run date or null
        # For simplicity, we get the latest salary structure for each staff (you can refine)
        staff_list = Staff.objects.filter(status='Active')
        entries = []
        total_gross = Decimal('0.00')
        total_deductions = Decimal('0.00')
        total_net = Decimal('0.00')

        for staff in staff_list:
            # Get the salary structure effective at the run's month (we assume effective_from <= run month)
            # Simplified: get the latest one by effective_from
            salary_struct = staff.salary_structures.order_by('-effective_from').first()
            if not salary_struct:
                continue
            gross = salary_struct.gross_salary

            # Calculate deductions
            paye = calculate_paye(gross, settings.paye_brackets)
            nhif = calculate_nhif(gross, settings.nhif_schedule)
            nssf = calculate_nssf(gross, settings.nssf_tier1_limit, settings.nssf_tier1_rate,
                                   settings.nssf_tier2_limit, settings.nssf_tier2_rate)
            shif = calculate_shif(gross, settings.shaf_rate)  # SHIF rate (formerly SHA)
            housing = calculate_housing_levy(gross, settings.housing_levy_rate)
            other_deductions = Decimal('0.00')  # placeholder

            total_ded = paye + nhif + nssf + shif + housing + other_deductions
            net = gross - total_ded

            entry = PayrollEntry(
                payroll_run=payroll_run,
                staff=staff,
                salary_structure=salary_struct,
                gross_salary=gross,
                paye_tax=paye,
                nhif_deduction=nhif,
                nssf_deduction=nssf,
                shaf_deduction=shif,
                housing_levy=housing,
                other_deductions=other_deductions,
                payment_status='pending'
            )
            entries.append(entry)
            total_gross += gross
            total_deductions += total_ded
            total_net += net

        # Bulk create entries
        if entries:
            PayrollEntry.objects.bulk_create(entries)

        # Update run totals and status
        payroll_run.total_gross = total_gross
        payroll_run.total_deductions = total_deductions
        payroll_run.total_net = total_net
        payroll_run.status = 'completed'
        payroll_run.processed_at = timezone.now()
        payroll_run.save()

        return Response({'status': 'processed', 'entries_count': len(entries)})

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def pay(self, request, pk=None):
        payroll_run = self.get_object()
        if payroll_run.status != 'completed':
            return Response({'error': 'Only completed runs can be paid'}, status=status.HTTP_400_BAD_REQUEST)
        if payroll_run.status == 'paid':
            return Response({'error': 'Run already paid'}, status=status.HTTP_400_BAD_REQUEST)

        entries = payroll_run.entries.filter(payment_status='pending')
        if not entries.exists():
            return Response({'error': 'No pending entries to pay'}, status=400)

        # Simulate payment processing; in real scenario, call external API.
        failed_entries = []
        for entry in entries:
            # Simulate success/failure (here always success)
            try:
                # In production, replace with actual M-Pesa B2C or bank API call.
                # If API returns failure, append to failed_entries and set payment_status='failed'.
                PayrollPaymentLog.objects.create(
                    payroll_entry=entry,
                    amount=entry.net_pay,
                    payment_method=entry.salary_structure.payment_method,
                    destination=entry.staff.phone if entry.salary_structure.payment_method == 'mpesa' else entry.staff.bank_account_number,
                    status='completed',   # or 'failed'
                    processed_by=request.user.staff_profile
                )
                entry.payment_status = 'completed'
                entry.save(update_fields=['payment_status'])
            except Exception:
                entry.payment_status = 'failed'
                entry.save(update_fields=['payment_status'])
                failed_entries.append(entry.id)

        payroll_run.status = 'paid' if not failed_entries else 'partial_paid'
        payroll_run.paid_at = timezone.now()
        payroll_run.save()

        return Response({
            'status': 'paid' if not failed_entries else 'partial_paid',
            'entries_paid': entries.count() - len(failed_entries),
            'failed_entries': failed_entries
        })

class PayrollEntryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PayrollEntry.objects.all()
    serializer_class = PayrollEntrySerializer
    permission_classes = [IsBursar | IsAdmin]

class PayrollPaymentLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PayrollPaymentLog.objects.all()
    serializer_class = PayrollPaymentLogSerializer
    permission_classes = [IsBursar | IsAdmin]


class PayrollEntryPayslipView(APIView):
    permission_classes = [IsBursar | IsAdmin]

    def get(self, request, entry_id):
        try:
            entry = PayrollEntry.objects.select_related('staff', 'salary_structure', 'payroll_run__academic_year').get(id=entry_id)
        except PayrollEntry.DoesNotExist:
            return Response({'error': 'Payroll entry not found'}, status=status.HTTP_404_NOT_FOUND)

        pdf_bytes = generate_payslip_pdf(entry)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="payslip_{entry.id}.pdf"'
        return response
    

class TeacherPayslipListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get(self, request):
        staff = request.user.staff_profile
        if not staff:
            return Response({'error': 'No staff profile linked'}, status=status.HTTP_404_NOT_FOUND)
        entries = PayrollEntry.objects.filter(staff=staff).order_by('-payroll_run__processed_at')
        serializer = PayrollEntrySerializer(entries, many=True)
        return Response(serializer.data)

class TeacherPayslipDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get(self, request, entry_id):
        try:
            entry = PayrollEntry.objects.select_related('staff', 'payroll_run').get(id=entry_id, staff=request.user.staff_profile)
        except PayrollEntry.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        pdf_bytes = generate_payslip_pdf(entry)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="payslip_{entry.id}.pdf"'
        return response
    
class PayrollRunSummaryView(APIView):
    permission_classes = [IsBursar | IsAdmin]

    def get(self, request, run_id):
        run = get_object_or_404(PayrollRun, id=run_id)
        entries = run.entries.select_related('staff__department')
        dept_totals = {}
        for entry in entries:
            dept = entry.staff.department.name if entry.staff.department else 'Unknown'
            dept_totals[dept] = dept_totals.get(dept, 0) + entry.net_pay

        data = {
            'total_gross': run.total_gross,
            'total_deductions': run.total_deductions,
            'total_net': run.total_net,
            'entries_count': entries.count(),
            'department_net_pay_breakdown': dept_totals
        }
        return Response(data)
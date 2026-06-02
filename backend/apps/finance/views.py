import uuid
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, F
from decimal import Decimal
from django.db import transaction
from .models import (
    FeeInvoice, Payment, Expense, ExpenseCategory, ReconciliationLog, StudentCredit
)
from .serializers import (
    FeeInvoiceSerializer, PaymentSerializer, ExpenseSerializer,
    ExpenseCategorySerializer, ReconciliationLogSerializer, StudentCreditSerializer
)
from apps.accounts.permissions import IsBursar, IsAdmin
from django.http import HttpResponse
from django.conf import settings
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from .receipt_utils import generate_receipt_pdf



# ----------------------------------------------------------------------
# Invoice ViewSet (with credit application)
# ----------------------------------------------------------------------
class FeeInvoiceViewSet(viewsets.ModelViewSet):
    queryset = FeeInvoice.objects.all()
    serializer_class = FeeInvoiceSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['bursar', 'admin', 'principal']:
            return FeeInvoice.objects.all()
        elif user.role == 'parent' and user.student_profile:
            return FeeInvoice.objects.filter(student=user.student_profile)
        return FeeInvoice.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsBursar | IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Save the invoice first
        invoice = serializer.save(created_by=self.request.user.staff_profile)
        # Then apply any existing credits for this student
        self.apply_credits(invoice)

    def apply_credits(self, invoice):
        """Apply unused credits to the given invoice."""
        student = invoice.student
        credits = StudentCredit.objects.filter(
            student=student,
            used_amount__lt=F('amount')
        ).order_by('created_at')

        for credit in credits:
            remaining_credit = credit.amount - credit.used_amount
            if remaining_credit <= 0:
                continue
            # How much of the credit can be applied to this invoice
            remaining_due = invoice.total_amount - invoice.paid_amount
            if remaining_due <= 0:
                break
            apply_amount = min(remaining_credit, remaining_due)
            if apply_amount <= 0:
                continue

            # Create a payment of type 'credit'
            Payment.objects.create(
                transaction_reference=f"CREDIT-{credit.id}-{invoice.invoice_number}",
                student=student,
                invoice=invoice,
                amount=apply_amount,
                payment_method='credit',
                payment_channel='manual',
                status='completed',
                recorded_by=self.request.user.staff_profile,
                notes=f"Applied from credit {credit.id}"
            )
            # Update invoice paid amount and status
            invoice.paid_amount += apply_amount
            if invoice.paid_amount >= invoice.total_amount:
                invoice.status = 'paid'
            invoice.save(update_fields=['paid_amount', 'status'])
            # Update credit used amount
            credit.used_amount += apply_amount
            credit.save(update_fields=['used_amount'])


# ----------------------------------------------------------------------
# Payment ViewSet (with overpayment handling)
# ----------------------------------------------------------------------
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['bursar', 'admin', 'principal']:
            return Payment.objects.all()
        elif user.role == 'parent' and user.student_profile:
            return Payment.objects.filter(student=user.student_profile)
        return Payment.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsBursar | IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @transaction.atomic
    def perform_create(self, serializer):
        # Generate transaction reference if missing
        if not serializer.validated_data.get('transaction_reference'):
            serializer.validated_data['transaction_reference'] = str(uuid.uuid4())[:8].upper()
        payment = serializer.save(recorded_by=self.request.user.staff_profile)

        student = payment.student
        invoices = FeeInvoice.objects.filter(student=student, status__in=['sent', 'partially_paid'])
        total_due = invoices.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        total_paid = invoices.aggregate(paid=Sum('paid_amount'))['paid'] or Decimal('0.00')
        outstanding = total_due - total_paid

        if payment.amount > outstanding:
            excess = payment.amount - outstanding
            StudentCredit.objects.create(
                student=student,
                amount=excess,
                created_by=self.request.user.staff_profile,
                notes=f"Overpayment from {payment.transaction_reference}"
            )


# ----------------------------------------------------------------------
# Expense Category ViewSet
# ----------------------------------------------------------------------
class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsBursar | IsAdmin]


# ----------------------------------------------------------------------
# Expense ViewSet
# ----------------------------------------------------------------------
class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['bursar', 'admin', 'principal']:
            return Expense.objects.all()
        return Expense.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsBursar | IsAdmin]
        elif self.action == 'approve':
            permission_classes = [IsAdmin | IsBursar]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.staff_profile)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        expense = self.get_object()
        if expense.status != 'pending':
            return Response(
                {'error': 'Expense not in pending state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        expense.status = 'approved'
        expense.approved_by = request.user.staff_profile
        expense.approved_at = timezone.now()
        expense.save()
        return Response({'status': 'approved'})


# ----------------------------------------------------------------------
# Reconciliation Log ViewSet
# ----------------------------------------------------------------------
class ReconciliationLogViewSet(viewsets.ModelViewSet):
    queryset = ReconciliationLog.objects.all()
    serializer_class = ReconciliationLogSerializer
    permission_classes = [IsBursar | IsAdmin]

    def perform_create(self, serializer):
        serializer.save(reconciled_by=self.request.user.staff_profile)

class StudentCreditViewSet(viewsets.ModelViewSet):
    queryset = StudentCredit.objects.all()
    serializer_class = StudentCreditSerializer
    permission_classes = [IsBursar | IsAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['bursar', 'admin', 'principal']:
            return StudentCredit.objects.all()
        elif user.role == 'parent' and user.student_profile:
            return StudentCredit.objects.filter(student=user.student_profile)
        return StudentCredit.objects.none()


# In apps/finance/views.py, replace the existing PaymentReceiptView with:

from .receipt_utils import generate_receipt_pdf   # import the utility

class PaymentReceiptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.select_related('invoice', 'student').get(id=payment_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if user.role in ['bursar', 'admin', 'principal']:
            pass
        elif user.role == 'parent':
            if not user.student_profile or payment.student != user.student_profile:
                return Response({'error': 'You can only view receipts for your own children'}, status=403)
        else:
            return Response({'error': 'Permission denied'}, status=403)

        pdf_bytes = generate_receipt_pdf(payment)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="receipt_{payment.id}.pdf"'
        return response
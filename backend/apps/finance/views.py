from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    FeeInvoice, Payment, Expense, ExpenseCategory
)
from .serializers import (
    FeeInvoiceSerializer, PaymentSerializer, ExpenseSerializer, ExpenseCategorySerializer
)
from apps.accounts.permissions import IsBursar, IsAdmin, IsStaffOrAdmin


class FeeInvoiceViewSet(viewsets.ModelViewSet):
    queryset = FeeInvoice.objects.all()   # ADD THIS
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
        serializer.save(created_by=self.request.user.staff_profile)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()   # ADD THIS
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

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user.staff_profile)


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsBursar | IsAdmin]


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()   # ADD THIS
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
            return Response({'error': 'Expense not in pending state'}, status=status.HTTP_400_BAD_REQUEST)
        expense.status = 'approved'
        expense.approved_by = request.user.staff_profile
        expense.approved_at = timezone.now()
        expense.save()
        return Response({'status': 'approved'})
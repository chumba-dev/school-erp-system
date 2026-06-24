from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from decimal import Decimal
from .models import BudgetPeriod, BudgetCategory, BudgetLineItem
from .serializers import (
    BudgetPeriodSerializer, BudgetCategorySerializer, BudgetLineItemSerializer
)
from apps.accounts.permissions import IsBursar, IsAdmin
from apps.finance.models import Payment
from apps.payroll.models import PayrollEntry
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from apps.audit.utils import log_custom_action

# Helper: compute actual amount for a line item
def compute_actual_amount(line_item):
    period = line_item.budget_period
    cat = line_item.category
    start = period.start_date
    end = period.end_date

    if cat.type == 'revenue':
        # Sum of payments (completed) within the period for all students (no direct category mapping)
        # For simplicity, we sum all completed payments within the period.
        # In a real system, you might need to map categories to specific fee types.
        total = Payment.objects.filter(
            status='completed',
            payment_date__date__range=(start, end)
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        return total
    else:  # expenditure
        # Sum of expenses (paid status) within the period
        from apps.finance.models import Expense
        expense_total = Expense.objects.filter(
            status='paid',
            expense_date__range=(start, end)
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        # Sum of payroll entries (paid runs) within the period
        payroll_total = PayrollEntry.objects.filter(
            payment_status='completed',
            payroll_run__paid_at__date__range=(start, end)
        ).aggregate(total=Sum('net_pay'))['total'] or Decimal('0.00')
        return expense_total + payroll_total

class BudgetPeriodViewSet(viewsets.ModelViewSet):
    queryset = BudgetPeriod.objects.all()
    serializer_class = BudgetPeriodSerializer
    permission_classes = [IsBursar | IsAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['academic_year', 'term', 'status']

    def perform_create(self, serializer):
        # You can add validation here (e.g., no overlapping active periods)
        serializer.save()

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        period = self.get_object()
        if period.status != 'draft':
            return Response({'error': 'Only draft budgets can be activated'}, status=400)
        old_status = period.status
        period.status = 'active'
        period.save()
        log_custom_action(
            action='ACTIVATE',
            table_name='budget_budgetperiod',
            record_id=period.id,
            old_values={'status': old_status},
            new_values={'status': period.status}
        )
        return Response({'status': 'activated'})

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        period = self.get_object()
        if period.status != 'active':
            return Response({'error': 'Only active budgets can be closed'}, status=400)
        old_status = period.status
        period.status = 'closed'
        period.save()
        log_custom_action(
            action='CLOSE',
            table_name='budget_budgetperiod',
            record_id=period.id,
            old_values={'status': old_status},
            new_values={'status': period.status}
        )
        return Response({'status': 'closed'})
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == 'closed':
            raise PermissionDenied("Cannot modify a closed budget period.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != 'draft':
            raise PermissionDenied("Only draft budgets can be deleted.")
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        period = self.get_object()
        line_items = period.line_items.select_related('category')
        revenue_planned = Decimal('0.00')
        revenue_actual = Decimal('0.00')
        expenditure_planned = Decimal('0.00')
        expenditure_actual = Decimal('0.00')

        for item in line_items:
            actual = compute_actual_amount(item)   # dynamic computation
            if item.category.type == 'revenue':
                revenue_planned += item.planned_amount
                revenue_actual += actual
            else:
                expenditure_planned += item.planned_amount
                expenditure_actual += actual

        data = {
            'budget_period': {
                'id': str(period.id),
                'name': period.name,
                'status': period.status,
                'start_date': period.start_date,
                'end_date': period.end_date,
            },
            'revenue': {
                'planned': revenue_planned,
                'actual': revenue_actual,
                'variance': revenue_actual - revenue_planned,
            },
            'expenditure': {
                'planned': expenditure_planned,
                'actual': expenditure_actual,
                'variance': expenditure_actual - expenditure_planned,
            },
            'net': {
                'planned': revenue_planned - expenditure_planned,
                'actual': revenue_actual - expenditure_actual,
                'variance': (revenue_actual - expenditure_actual) - (revenue_planned - expenditure_planned),
            }
        }
        return Response(data)

class BudgetCategoryViewSet(viewsets.ModelViewSet):
    queryset = BudgetCategory.objects.all()
    serializer_class = BudgetCategorySerializer
    permission_classes = [IsBursar | IsAdmin]

class BudgetLineItemViewSet(viewsets.ModelViewSet):
    queryset = BudgetLineItem.objects.all()
    serializer_class = BudgetLineItemSerializer
    permission_classes = [IsBursar | IsAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        period_id = self.request.query_params.get('budget_period')
        if period_id:
            queryset = queryset.filter(budget_period_id=period_id)
        return queryset
    
    def _check_period_editable(self, budget_period):
        if budget_period.status == 'closed':
            raise PermissionDenied("Cannot modify line items for a closed budget period.")

    def perform_create(self, serializer):
        budget_period = serializer.validated_data.get('budget_period')
        self._check_period_editable(budget_period)
        serializer.save()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        self._check_period_editable(instance.budget_period)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self._check_period_editable(instance.budget_period)
        return super().destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        # Dynamically compute actual_amount when retrieving
        instance = self.get_object()
        actual = compute_actual_amount(instance)
        # Update the instance's actual_amount (optional: save to DB for caching)
        # For now, just override the field in the serialized data
        serializer = self.get_serializer(instance)
        data = serializer.data
        data['actual_amount'] = str(actual)
        data['variance'] = str(actual - instance.planned_amount)
        return Response(data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # For efficiency, you might want to prefetch and compute in loop, but keep simple
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        for item, obj in zip(data, queryset):
            actual = compute_actual_amount(obj)
            item['actual_amount'] = str(actual)
            item['variance'] = str(actual - obj.planned_amount)
        return Response(data)

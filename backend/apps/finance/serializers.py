from rest_framework import serializers
from .models import (
    FeeInvoice, InvoiceLineItem, Payment, PaymentAllocation,
    Expense, ExpensePayment, ExpenseCategory, ReconciliationLog, StudentCredit
)


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLineItem
        fields = ['id', 'description', 'amount', 'category', 'is_lost_book', 'book_number']


class FeeInvoiceSerializer(serializers.ModelSerializer):
    line_items = InvoiceLineItemSerializer(many=True, read_only=True)
    balance_due = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = FeeInvoice
        fields = [
            'id', 'invoice_number', 'student', 'academic_year', 'term',
            'due_date', 'status', 'total_amount', 'paid_amount', 'balance_due',
            'notes', 'created_by', 'created_at', 'updated_at', 'line_items'
        ]
        read_only_fields = ['invoice_number', 'created_by', 'created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_reference', 'student', 'invoice', 'amount',
            'payment_method', 'payment_channel', 'status', 'mpesa_receipt',
            'recorded_by', 'payment_date', 'notes'
        ]
        read_only_fields = ['transaction_reference', 'recorded_by', 'payment_date']


class PaymentAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAllocation
        fields = ['id', 'payment', 'invoice', 'amount_allocated']


class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = ['id', 'name', 'description']


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            'id', 'expense_number', 'title', 'category', 'amount', 'paid_amount',
            'status', 'payee_name', 'payee_phone', 'payee_bank', 'payee_account',
            'expense_date', 'created_by', 'approved_by', 'approved_at', 'notes'
        ]
        read_only_fields = ['expense_number', 'created_by', 'approved_at']


class ExpensePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpensePayment
        fields = [
            'id', 'expense', 'amount', 'payment_method', 'transaction_reference',
            'status', 'processed_by', 'processed_at', 'mpesa_receipt'
        ]
        read_only_fields = ['processed_by', 'processed_at']

class ReconciliationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReconciliationLog
        fields = '__all__'
        read_only_fields = ['reconciled_by', 'reconciled_at']

class StudentCreditSerializer(serializers.ModelSerializer):
    remaining = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = StudentCredit
        fields = ['id', 'student', 'amount', 'used_amount', 'remaining', 'created_by', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']
from rest_framework import serializers
from .models import BudgetPeriod, BudgetCategory, BudgetLineItem
from apps.academics.models import AcademicYear, Term

class BudgetPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetPeriod
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class BudgetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategory
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class BudgetLineItemSerializer(serializers.ModelSerializer):
    variance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = BudgetLineItem
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'actual_amount', 'variance')
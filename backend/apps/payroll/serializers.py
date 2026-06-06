from rest_framework import serializers
from .models import (
    SalaryStructure, PayrollDeductionSetting, PayrollRun, PayrollEntry, PayrollPaymentLog
)

class SalaryStructureSerializer(serializers.ModelSerializer):
    gross_salary = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = SalaryStructure
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class PayrollDeductionSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollDeductionSetting
        fields = '__all__'

class PayrollEntrySerializer(serializers.ModelSerializer):
    total_deductions = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    net_pay = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = PayrollEntry
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'total_deductions', 'net_pay')

class PayrollPaymentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollPaymentLog
        fields = '__all__'
        read_only_fields = ('id', 'processed_at')

class PayrollRunSerializer(serializers.ModelSerializer):
    entries = PayrollEntrySerializer(many=True, read_only=True)
    total_gross = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total_deductions = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total_net = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = PayrollRun
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'processed_at', 'paid_at', 
                            'total_gross', 'total_deductions', 'total_net')
from django.db import models
from apps.common.models import BaseModel, SoftDeleteModel
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

class SalaryStructure(BaseModel):
    staff = models.ForeignKey('core.Staff', on_delete=models.CASCADE, related_name='salary_structures')
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    housing_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    transport_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    medical_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    other_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    payment_method = models.CharField(max_length=20, choices=[('mpesa', 'M-Pesa'), ('bank', 'Bank Transfer')])

    @property
    def gross_salary(self):
        return self.basic_salary + self.housing_allowance + self.transport_allowance + self.medical_allowance + self.other_allowances

    def __str__(self):
        return f"{self.staff} - effective {self.effective_from}"
    
    def clean(self):
        if self.effective_to and self.effective_from >= self.effective_to:
            raise ValidationError({'effective_to': 'Effective to must be after effective from.'})
        if self.effective_from > timezone.now().date():
            raise ValidationError({'effective_from': 'Effective from cannot be in the future.'})
        if any(v < 0 for v in [self.basic_salary, self.housing_allowance, self.transport_allowance, self.medical_allowance, self.other_allowances]):
            raise ValidationError('Salary components cannot be negative.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class PayrollDeductionSetting(BaseModel):
    effective_year = models.IntegerField(unique=True)
    shaf_rate = models.DecimalField(max_digits=5, decimal_places=2, default=2.75)   # 2.75%
    housing_levy_rate = models.DecimalField(max_digits=5, decimal_places=2, default=1.5) # 1.5%
    nssf_tier1_rate = models.DecimalField(max_digits=5, decimal_places=2, default=6.0)
    nssf_tier1_limit = models.DecimalField(max_digits=10, decimal_places=2, default=8000)
    nssf_tier2_rate = models.DecimalField(max_digits=5, decimal_places=2, default=6.0)
    nssf_tier2_limit = models.DecimalField(max_digits=10, decimal_places=2, default=72000)
    nhif_schedule = models.JSONField()   # e.g., {"0-5999":150, "6000-7999":300, ...}
    paye_brackets = models.JSONField()   # e.g., [{"up_to": 24000, "rate":10}, ...]

    def __str__(self):
        return f"Settings for {self.effective_year}"

class PayrollRun(BaseModel):
    STATUS_CHOICES = [('draft', 'Draft'), ('processing', 'Processing'), ('completed', 'Completed'), ('paid', 'Paid')]
    run_number = models.CharField(max_length=50, unique=True)
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.RESTRICT)
    term = models.ForeignKey('academics.Term', on_delete=models.RESTRICT, null=True, blank=True)
    month = models.IntegerField()  # 1-12
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_gross = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_net = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    processed_by = models.ForeignKey('core.Staff', on_delete=models.RESTRICT, related_name='payroll_runs')
    processed_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.run_number} - {self.academic_year.year} month {self.month}"
    
    def clean(self):
        if self.total_gross < 0 or self.total_deductions < 0 or self.total_net < 0:
            raise ValidationError('Totals cannot be negative.')

    class Meta:
        unique_together = ['academic_year', 'month']
        constraints = [
            models.CheckConstraint(condition=models.Q(month__gte=1, month__lte=12), name='valid_month')
        ]

class PayrollEntry(BaseModel):
    PAYMENT_STATUS = [('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')]
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='entries')
    staff = models.ForeignKey('core.Staff', on_delete=models.RESTRICT)
    salary_structure = models.ForeignKey(SalaryStructure, on_delete=models.RESTRICT)
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)
    paye_tax = models.DecimalField(max_digits=12, decimal_places=2)
    nhif_deduction = models.DecimalField(max_digits=12, decimal_places=2)
    nssf_deduction = models.DecimalField(max_digits=12, decimal_places=2)
    shaf_deduction = models.DecimalField(max_digits=12, decimal_places=2)
    housing_levy = models.DecimalField(max_digits=12, decimal_places=2)
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_reference = models.CharField(max_length=100, blank=True)

    @property
    def total_deductions(self):
        return self.paye_tax + self.nhif_deduction + self.nssf_deduction + self.shaf_deduction + self.housing_levy + self.other_deductions

    @property
    def net_pay(self):
        return self.gross_salary - self.total_deductions

class PayrollPaymentLog(BaseModel):
    payroll_entry = models.ForeignKey(PayrollEntry, on_delete=models.CASCADE, related_name='payment_logs')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=[('mpesa', 'M-Pesa B2C'), ('bank', 'Bank Transfer')])
    destination = models.CharField(max_length=100)  # phone or account number
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending')
    mpesa_receipt = models.CharField(max_length=50, blank=True)
    processed_by = models.ForeignKey('core.Staff', on_delete=models.RESTRICT)
    processed_at = models.DateTimeField(default=models.functions.Now())

    def __str__(self):
        return f"Payment for {self.payroll_entry.staff} - {self.amount}"
    

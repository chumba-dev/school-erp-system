from django.db import models
from apps.common.models import BaseModel
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal

class BudgetPeriod(BaseModel):
    name = models.CharField(max_length=100)
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.RESTRICT, related_name='budget_periods')
    term = models.ForeignKey('academics.Term', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('draft', 'Draft'), ('active', 'Active'), ('closed', 'Closed')], default='draft')
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.academic_year.year})"

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError({'end_date': 'End date must be after start date.'})
        # Optionally ensure active budget is unique per academic_year/term, but that's optional

    def save(self, *args, **kwargs):
        self.full_clean()  # calls clean() before saving
        super().save(*args, **kwargs)    

class BudgetCategory(BaseModel):
    TYPE_CHOICES = [('revenue', 'Revenue'), ('expenditure', 'Expenditure')]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        unique_together = ['name', 'type', 'parent']   # ensures (name, type, parent) is unique
        # This prevents duplicate categories of the same type under the same parent.

    def __str__(self):
        return self.name

class BudgetLineItem(BaseModel):
    budget_period = models.ForeignKey(BudgetPeriod, on_delete=models.CASCADE, related_name='line_items')
    category = models.ForeignKey(BudgetCategory, on_delete=models.RESTRICT)
    planned_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    actual_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    @property
    def variance(self):
        return self.actual_amount - self.planned_amount

    def __str__(self):
        return f"{self.budget_period.name} - {self.category.name}"
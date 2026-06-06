from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PayrollRun
from apps.audit.models import AuditLog

@receiver(post_save, sender=PayrollRun)
def log_payroll_run_change(sender, instance, created, **kwargs):
    if created:
        action = 'CREATE'
    else:
        action = 'UPDATE'
    AuditLog.objects.create(
        user_id=None,  # can get from request context later; for now, track via middleware
        user_role=None,
        action=action,
        table_name='payroll_payrollrun',
        record_id=instance.id,
        new_values={'status': instance.status, 'run_number': instance.run_number}
    )
from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from .models import AuditLog
from .middleware import get_current_user, get_current_ip

AUDIT_MODELS = (
    'auth.user', 'core.student', 'core.staff',
    'finance.feeinvoice', 'finance.payment', 'finance.expense',
    'payroll.payrollrun', 'payroll.salarystructure',
    'budget.budgetperiod', 'budget.budgetlineitem',
    'integration.apikey', 'integration.lostbookevent'
)

@receiver(pre_save)
def capture_old_values(sender, instance, **kwargs):
    app_label = sender._meta.app_label
    model_name = sender._meta.model_name
    full_name = f"{app_label}.{model_name}"
    if full_name not in AUDIT_MODELS:
        return
    if instance.pk is None:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    old_data = {}
    new_data = {}
    for field in instance._meta.fields:
        field_name = field.name
        old_val = getattr(old, field_name)
        new_val = getattr(instance, field_name)
        if old_val != new_val:
            old_data[field_name] = str(old_val)
            new_data[field_name] = str(new_val)
    if old_data:
        instance._audit_old_values = old_data
        instance._audit_new_values = new_data
    else:
        instance._audit_old_values = None
        instance._audit_new_values = None

@receiver(post_save)
def log_create_update(sender, instance, created, **kwargs):
    print(f"[Audit] 1. Signal triggered for {sender._meta.db_table}, created={created}")
    
    app_label = sender._meta.app_label
    model_name = sender._meta.model_name
    full_name = f"{app_label}.{model_name}"
    print(f"[Audit] 2. full_name = {full_name}")
    
    if full_name not in AUDIT_MODELS:
        print(f"[Audit] 3. Skipping {full_name} (not in AUDIT_MODELS)")
        return
    print("[Audit] 4. Passed AUDIT_MODELS check")
    
    user = get_current_user()
    print(f"[Audit] 5. user = {user}")
    if not user:
        print("[Audit] 6. No user, skipping log")
        return
    print("[Audit] 7. User is valid, proceeding to create log")
    
    action = 'CREATE' if created else 'UPDATE'
    old_values = getattr(instance, '_audit_old_values', None)
    new_values = getattr(instance, '_audit_new_values', None)
    if created:
        old_values = None
        new_values = {f.name: str(getattr(instance, f.name)) for f in instance._meta.fields}
    else:
        if new_values is None:
            new_values = {f.name: str(getattr(instance, f.name)) for f in instance._meta.fields}

    try:
        log = AuditLog.objects.create(
            user=user,
            user_role=user.role if hasattr(user, 'role') else '',
            action=action,
            table_name=sender._meta.db_table,
            record_id=instance.pk,
            old_values=old_values,
            new_values=new_values,
            ip_address=get_current_ip()
        )
        print(f"[Audit] 8. Log created successfully with id {log.id}")
    except Exception as e:
        print(f"[Audit] 9. ERROR creating audit log: {e}")

@receiver(pre_delete)
def log_delete(sender, instance, **kwargs):
    app_label = sender._meta.app_label
    model_name = sender._meta.model_name
    full_name = f"{app_label}.{model_name}"
    if full_name not in AUDIT_MODELS:
        return
    user = get_current_user()
    if not user:
        return
    old_values = {f.name: str(getattr(instance, f.name)) for f in instance._meta.fields if f.name != 'id'}
    AuditLog.objects.create(
        user=user,
        user_role=user.role if hasattr(user, 'role') else '',
        action='DELETE',
        table_name=sender._meta.db_table,
        record_id=instance.pk,
        old_values=old_values,
        new_values=None,
        ip_address=get_current_ip()
    )
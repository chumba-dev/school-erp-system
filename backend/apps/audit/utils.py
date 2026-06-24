from .models import AuditLog
from .middleware import get_current_user, get_current_ip
from apps.reporting.utils import generate_pdf_report, generate_excel_report, generate_csv_report

def log_custom_action(action, table_name, record_id, old_values=None, new_values=None):
    """
    Log a custom action (APPROVE, PAY, ACTIVATE, CLOSE, REVOKE, etc.)
    """
    user = get_current_user()
    if not user:
        return  # Skip if no user (e.g., system actions)
    AuditLog.objects.create(
        user=user,
        user_role=user.role if hasattr(user, 'role') else '',
        action=action,
        table_name=table_name,
        record_id=record_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=get_current_ip()
    )
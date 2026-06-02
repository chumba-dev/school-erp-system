import threading
from django.core.mail import EmailMessage
from django.conf import settings
from .receipt_utils import generate_receipt_pdf

def send_receipt_email(payment):
    """Send receipt as email attachment to parent."""
    parent_email = payment.student.parent_email
    if not parent_email:
        return
    subject = f"Payment Receipt - Invoice {payment.invoice.invoice_number}"
    body = (
        f"Dear Parent,\n\n"
        f"Thank you for your payment of KES {payment.amount:.2f}.\n"
        f"Invoice: {payment.invoice.invoice_number}\n"
        f"Transaction Ref: {payment.transaction_reference}\n\n"
        f"Receipt attached.\n\n"
        f"Regards,\nSchool Bursar"
    )
    pdf_bytes = generate_receipt_pdf(payment)
    email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [parent_email])
    email.attach(f"receipt_{payment.id}.pdf", pdf_bytes, 'application/pdf')
    email.send()

def send_receipt_email_async(payment):
    """Send email in background thread to avoid blocking callback."""
    thread = threading.Thread(target=send_receipt_email, args=(payment,))
    thread.start()
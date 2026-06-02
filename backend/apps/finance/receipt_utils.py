import qrcode
import tempfile
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from django.conf import settings

def generate_receipt_pdf(payment):
    invoice = payment.invoice
    student = payment.student

    school_name = getattr(settings, 'SCHOOL_NAME', 'Kitondo School')
    school_address = getattr(settings, 'SCHOOL_ADDRESS', 'P.O. Box 123, Kitondo, Kenya')

    receipt_number = f"RCP-{payment.id.hex[:8].upper()}"
    payment_date = payment.payment_date.strftime('%Y-%m-%d %H:%M:%S')
    student_name = f"{student.first_name} {student.last_name}"
    admission_number = student.admission_number
    invoice_number = invoice.invoice_number if invoice else 'N/A'
    payment_method = payment.get_payment_method_display()
    transaction_ref = payment.transaction_reference
    amount_paid = payment.amount
    balance_due = invoice.balance_due if invoice else 0

    # --- QR code as temporary file ---
    qr_text = f"Receipt: {receipt_number} | Amount: KES {amount_paid:.2f} | Date: {payment_date} | Student: {admission_number}"
    qr_img = qrcode.make(qr_text)
    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    tmp.close()
    qr_img.save(tmp.name, format='PNG')
    qr_flowable = Image(tmp.name, width=3*cm, height=3*cm)

    # --- PDF construction ---
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', parent=styles['Heading1'],
                                 alignment=TA_CENTER, spaceAfter=12)
    normal_style = styles['Normal']
    story = []

    # Header
    story.append(Paragraph(school_name, title_style))
    story.append(Paragraph(school_address, styles['Heading4']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("OFFICIAL RECEIPT", title_style))
    story.append(Spacer(1, 0.5*cm))

    # Details table
    data = [
        ["Receipt No:", receipt_number],
        ["Payment Date:", payment_date],
        ["Student Name:", f"{student_name} ({admission_number})"],
        ["Invoice No:", invoice_number],
        ["Payment Method:", payment_method],
        ["Transaction Ref:", transaction_ref],
    ]
    table = Table(data, colWidths=[4*cm, 10*cm])
    table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (0,-1), 'RIGHT'),
        ('ALIGN', (1,0), (1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3*cm))

    # QR code table (right-aligned)
    qr_table = Table([[qr_flowable]], colWidths=[14*cm])
    qr_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(qr_table)
    story.append(Spacer(1, 0.5*cm))

    # Line items
    if invoice and invoice.line_items.exists():
        items_data = [["Description", "Amount (KES)"]]
        for item in invoice.line_items.all():
            items_data.append([item.description, f"{item.amount:.2f}"])
        items_data.append(["Total Paid", f"{amount_paid:.2f}"])
        items_table = Table(items_data, colWidths=[10*cm, 4*cm])
        items_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        story.append(items_table)
    else:
        story.append(Paragraph(f"Amount Paid: KES {amount_paid:.2f}", normal_style))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"<b>Balance Due:</b> KES {balance_due:.2f}", normal_style))
    story.append(Spacer(1, 1*cm))

    # Footer
    footer_style = ParagraphStyle(name='Footer', parent=normal_style, alignment=TA_CENTER, fontSize=8)
    story.append(Paragraph("This is a computer-generated receipt. No signature required.", footer_style))
    story.append(Paragraph("Thank you for your payment.",
                           ParagraphStyle(name='Footer2', parent=normal_style,
                                          alignment=TA_CENTER, fontSize=9, textColor=colors.grey)))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()

    # Clean up temporary QR file
    os.unlink(tmp.name)

    return pdf
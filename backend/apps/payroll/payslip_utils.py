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

def generate_payslip_pdf(payroll_entry):
    """
    Generate a PDF payslip for a payroll entry.
    """
    staff = payroll_entry.staff
    salary_struct = payroll_entry.salary_structure
    run = payroll_entry.payroll_run

    school_name = getattr(settings, 'SCHOOL_NAME', 'Kitondo School')
    school_address = getattr(settings, 'SCHOOL_ADDRESS', 'P.O. Box 123, Kitondo, Kenya')

    payslip_number = f"PS-{payroll_entry.id.hex[:8].upper()}"
    payment_date = run.paid_at.strftime('%Y-%m-%d') if run.paid_at else run.processed_at.strftime('%Y-%m-%d')
    staff_name = f"{staff.first_name} {staff.last_name}"
    staff_tsc = staff.tsc_number
    gross = payroll_entry.gross_salary
    paye = payroll_entry.paye_tax
    nhif = payroll_entry.nhif_deduction
    nssf = payroll_entry.nssf_deduction
    shif = payroll_entry.shaf_deduction
    housing = payroll_entry.housing_levy
    other = payroll_entry.other_deductions
    total_deductions = payroll_entry.total_deductions
    net_pay = payroll_entry.net_pay

    # QR code data (plain text summary)
    qr_text = f"Payslip: {payslip_number} | Staff: {staff_tsc} | Month: {run.month}/{run.academic_year.year} | Net Pay: KES {net_pay:.2f}"
    qr_img = qrcode.make(qr_text)
    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    tmp.close()
    qr_img.save(tmp.name, format='PNG')
    qr_flowable = Image(tmp.name, width=3*cm, height=3*cm)

    # PDF construction
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
    story.append(Paragraph("PAYSLIP", title_style))
    story.append(Spacer(1, 0.5*cm))

    # Details table
    data = [
        ["Payslip No:", payslip_number],
        ["Payment Date:", payment_date],
        ["Staff Name:", staff_name],
        ["TSC No:", staff_tsc],
        ["Payroll Run:", run.run_number],
        ["Month:", f"{run.month}/{run.academic_year.year}"],
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

    # Salary breakdown table
    salary_data = [
        ["Basic Salary", f"{salary_struct.basic_salary:.2f}"],
        ["Housing Allowance", f"{salary_struct.housing_allowance:.2f}"],
        ["Transport Allowance", f"{salary_struct.transport_allowance:.2f}"],
        ["Medical Allowance", f"{salary_struct.medical_allowance:.2f}"],
        ["Other Allowances", f"{salary_struct.other_allowances:.2f}"],
        ["Gross Salary", f"{gross:.2f}"],
    ]
    salary_table = Table(salary_data, colWidths=[10*cm, 4*cm])
    salary_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    story.append(salary_table)
    story.append(Spacer(1, 0.3*cm))

    # Deductions table
    deductions_data = [
        ["PAYE Tax", f"{paye:.2f}"],
        ["NHIF", f"{nhif:.2f}"],
        ["NSSF", f"{nssf:.2f}"],
        ["SHIF (SHA)", f"{shif:.2f}"],
        ["Housing Levy", f"{housing:.2f}"],
        ["Other Deductions", f"{other:.2f}"],
        ["Total Deductions", f"{total_deductions:.2f}"],
    ]
    ded_table = Table(deductions_data, colWidths=[10*cm, 4*cm])
    ded_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    story.append(ded_table)
    story.append(Spacer(1, 0.3*cm))

    # Net pay
    story.append(Paragraph(f"<b>Net Pay: KES {net_pay:.2f}</b>", normal_style))
    story.append(Spacer(1, 0.5*cm))

    # QR code (right-aligned)
    qr_table = Table([[qr_flowable]], colWidths=[14*cm])
    qr_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(qr_table)
    story.append(Spacer(1, 1*cm))

    # Footer
    footer_style = ParagraphStyle(name='Footer', parent=normal_style,
                                  alignment=TA_CENTER, fontSize=8)
    story.append(Paragraph("This is a computer-generated payslip.", footer_style))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    # Clean up temporary QR file
    os.unlink(tmp.name)
    return pdf
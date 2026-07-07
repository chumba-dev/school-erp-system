from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from django.conf import settings
from django.db.models import Avg, Sum, Count

def generate_report_card(student, exam_results, term, academic_year):
    """
    Generate a PDF report card for a student.
    exam_results: queryset of ExamResult for that student in the given term/year.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', parent=styles['Heading1'], alignment=TA_CENTER, spaceAfter=12)
    normal_style = styles['Normal']

    school_name = getattr(settings, 'SCHOOL_NAME', 'Kitondo School')
    school_address = getattr(settings, 'SCHOOL_ADDRESS', 'P.O. Box 123, Kitondo')

    story = []

    # Header
    story.append(Paragraph(school_name, title_style))
    story.append(Paragraph(school_address, styles['Heading4']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("STUDENT REPORT CARD", title_style))
    story.append(Spacer(1, 0.5*cm))

    # Student info
    data = [
        ["Student Name:", f"{student.first_name} {student.last_name}"],
        ["Admission No:", student.admission_number],
        ["Class:", student.class_obj.name if student.class_obj else "N/A"],
        ["Term:", term.name],
        ["Academic Year:", str(academic_year.year)],
    ]
    info_table = Table(data, colWidths=[4*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5*cm))

    # Marks table
    marks_data = [["Subject", "Marks", "Grade", "Points"]]
    total_marks = 0
    total_points = 0
    for result in exam_results:
        marks_data.append([
            result.exam.subject.name,
            str(result.marks_obtained),
            result.grade,
            # You can also include points from GradeScale if needed
        ])
        total_marks += result.marks_obtained
        # We don't have points stored, but we can compute from grade scale later.
    # Add total row
    marks_data.append(["Total", str(total_marks), "", ""])
    # Compute mean (if number of subjects >0)
    subject_count = exam_results.count()
    if subject_count > 0:
        mean = total_marks / subject_count
        marks_data.append(["Mean Score", f"{mean:.2f}", "", ""])

    marks_table = Table(marks_data, colWidths=[8*cm, 3*cm, 3*cm, 3*cm])
    marks_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    story.append(marks_table)
    story.append(Spacer(1, 0.5*cm))

    # Comments (if any)
    comments = exam_results.filter(teacher_comment__isnull=False).first()
    if comments and comments.teacher_comment:
        story.append(Paragraph(f"<b>Teacher's Comment:</b> {comments.teacher_comment}", normal_style))
    principal_remark = exam_results.filter(principal_remark__isnull=False).first()
    if principal_remark and principal_remark.principal_remark:
        story.append(Paragraph(f"<b>Principal's Remark:</b> {principal_remark.principal_remark}", normal_style))

    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("This is a computer-generated report card.", styles['Italic']))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
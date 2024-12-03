
from django.conf import settings

import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle




from .my_utils import *




# import openai

# openai.api_key = settings.OPEN_AI_KEY

position = {
    'Proficient' : ('Teacher I', 'Teacher II', 'Teacher III'  ),
    'Highly Proficient' : ('Master Teacher I', 'Master Teacher II', 'Master Teacher III', 'Master Teacher IV'),
}

evaluator_positions = {
    "Proficient": ["Head Teacher I", "Head Teacher II", "Head Teacher III", "Head Teacher IV", "Head Teacher V", "Head Teacher VI"],
    "Highly Proficient": ["School Principal I", "School Principal II", "School Principal III", "School Principal IV"]
}




def generate_report_by_teacher(school : models.School , user : models.People):
     
    school_year_text = None
    school_year = models.IPCRFForm.objects.filter( school_id=school.school_id, form_type='PART 1').order_by('-created_at').first()
    if not school_year:
        school_year = models.COTForm.objects.filter(school_id=school.school_id).order_by('-created_at').first()
        if not school_year:
            school_year = models.RPMSFolder.objects.filter(school_id=school.school_id).order_by('-created_at').first()
            if not school_year:
                return None
            else:
                school_year_text = school_year.rpms_folder_school_year
        else:
            school_year_text = school_year.school_year
    else:
        school_year_text = school_year.school_year
    
    # Create a PDF buffer
    buffer = io.BytesIO()

    # Create a PDF document
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                            
        leftMargin=0.5 * inch, # Remove left margin
        rightMargin=0.5 * inch, # Remove right margin
        topMargin=0.5 * inch, # Remove top margin
        bottomMargin=0.5 * inch # Remove bottom margin
        
        )
    elements = []

    # Add logo/image in the center
    if school.school_logo:
        logo_path = settings.MEDIA_ROOT + '/' + school.school_logo.name
        logo = Image(logo_path, 2*inch, 2*inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    
    # Add School Name and School Year in the center
    styles = getSampleStyleSheet() 
    styles.add(ParagraphStyle(name='Center', alignment=1))  # 1 means center alignment
    styles.add(ParagraphStyle(name='Name', alignment=1, fontSize=18, fontName='Helvetica-Bold')) 
    styles.add(ParagraphStyle(name='SchoolYear', alignment=1, fontSize=16))

    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph(user.fullname, styles['Name']))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph(user.position, styles['SchoolYear']))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph(school_year_text, styles['SchoolYear']))

    elements.append(Spacer(1, 0.5*inch))
 
    # Add table headers
    recommendation = get_recommendation_result_with_percentage(employee_id=user.employee_id).get("result" , "Terminations")
    ipcrf = models.IPCRFForm.objects.filter(employee_id=user.employee_id, form_type='PART 1').order_by('-created_at').first()
    rating = ipcrf.evaluator_rating if ipcrf else 0
    performance_rating = classify_ipcrf_score(ipcrf.evaluator_rating if ipcrf else 0.0)
    job_years = user.get_job_years()
    qualified_rank = recommend_rank(user)
    table_data = [
        ["Performance Rating", "Final Rating", "Years of Experience", "Current Job Title", "Qualified Rank", "Recommendation"],
        [
            performance_rating, 
            round(rating, 2),
            f"{job_years.get('years')} year{'s' if job_years.get('years') > 1 else ''} and {job_years.get('months', 0)} month{'s' if job_years.get('months', 0) > 1 else ''}", 
            user.position , 
            qualified_rank[-1] if qualified_rank else "N\A", 
            recommendation
        ],
    ]
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#d6e0f5")),  # Light blue color for header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Text color for header
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align text
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold text for header
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Add table headers
    kras = ipcrf.get_information() if ipcrf else {}
    
    
    styles.add(ParagraphStyle(name='NormalLeftBold', alignment=0, fontName='Helvetica-Bold'))  # 0 means left alignment
    table_data2 = [
        [Paragraph("<b>INDIVIDUAL PERFORMANCE COMMITMENT AND REVIEW FORM</b>", styles['Center'])],
        [Paragraph("<b>Key Result Area</b>", styles['NormalLeftBold']), Paragraph("<b>Score</b>", styles['NormalLeftBold'])],
        ["KRA 1: Content Knowledge and Pedagogy", round(kras.get('kra1_evaluator', 0) , 2)],
        ["KRA 2: Learning and Environment and Diversity", round(kras.get('kra2_evaluator', 0) , 2)],
        ["KRA 3: Curriculum and Planning", round(kras.get('kra3_evaluator', 0) , 2)],
        ["KRA 4: Curriculum and Planning & Assessment", round(kras.get('kra4_evaluator', 0) , 2)],
        ["PLUS FACTOR",round(kras.get('plus_factor_evaluator', 0) , 2)],
        [Paragraph("<b>Final Rating</b>", styles['NormalLeftBold']), round(kras.get('evaluator_rating', 0) , 2)],
    ]


    table2 = Table(table_data2, colWidths=[4*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    table2.setStyle(TableStyle([
        ('SPAN', (0, 0), (-1, 0)),  # Span the first row across all columns
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#d6e0f5")),  # Light blue color for header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Text color for header
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align text
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold text for header
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table2)

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer and write it to the response.
    buffer.seek(0)
    return buffer
    # return HttpResponse(buffer, as_attachment=True, content_type='application/pdf')




from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.templatetags.static import static
from django.db.models.functions import ExtractYear
from django.utils import timezone
from django.conf import settings
from django.templatetags.static import static

from collections import defaultdict

from datetime import datetime

# Import requests first
import requests
from curl_cffi import requests as cf_reqs  # Import curl_cffi after requests


from g4f.client import Client
from uuid import uuid4
from . import models, forms_text

# import openai

# openai.api_key = settings.OPEN_AI_KEY

position = {
    'Proficient' : ('Teacher I', 'Teacher II', 'Teacher III'  ),
    'Highly Proficient' : ('Master Teacher I', 'Master Teacher II', 'Master Teacher III', 'Master Teacher IV'),
}

client = Client()

def generate_text(promt : str):
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "user", "content": promt}
    #     ]
    # )
    # return response.choices[0].message.content.strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": promt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"



def send_verification_email(user_email, verification_code , template , masbate_locker_email , subject, request):
    subject = subject 
    from_email = masbate_locker_email
    to_email = user_email
 
    deped_logo_url = request.build_absolute_uri(static('logo.png'))
    # Render the HTML template 
    html_content = render_to_string(template, {
        'verification_code': verification_code ,
        'deped_logo' : deped_logo_url
    })
    text_content = strip_tags(html_content)  # Create a plain text version

    # Create the email
    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()


def send_declined_reason(user_email, reason , template , masbate_locker_email , subject, request):
    subject = subject 
    from_email = masbate_locker_email
    to_email = user_email
 
    deped_logo_url = request.build_absolute_uri(static('logo.png'))
    # Render the HTML template 
    html_content = render_to_string(template, {
        'reason': reason ,
        'deped_logo' : deped_logo_url
    })
    text_content = strip_tags(html_content)  # Create a plain text version

    # Create the email
    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()


def send_account_info_email(user_email, username, password, template, from_email, subject):
    # Render the HTML template
    html_content = render_to_string(template, {
        'username': username,
        'password': password,
    })
    text_content = strip_tags(html_content)  # Create a plain text version

    # Create the email
    email = EmailMultiAlternatives(subject, text_content, from_email, [user_email])
    email.attach_alternative(html_content, "text/html")
    email.send()



def send_password_reset_email(user_email, verifiy_change_password_link, template, from_email, subject, request ):
    
    deped_logo_url = request.build_absolute_uri(static('logo.png'))
    html_content = render_to_string(template, {
        'verifiy_change_password_link': verifiy_change_password_link,
        'deped_logo' : deped_logo_url
    })
    text_content = strip_tags(html_content)  # Create a plain text version

    # Create the email
    email = EmailMultiAlternatives(subject, text_content, from_email, [user_email])
    email.attach_alternative(html_content, "text/html")
    email.send()


def parse_date_string(date_string):
    try:
        naive_datetime = datetime.strptime(date_string, "%B %d, %Y")
        parsed_date = timezone.make_aware(naive_datetime, timezone.get_current_timezone())
        return parsed_date
    except ValueError:
        print(f"Error: The date format of '{date_string}' is incorrect.")
        return None


def get_recommendation_result(employee_id : str):
    ipcrf_forms = models.IPCRFForm.objects.filter(employee_id=employee_id, form_type='PART 1').order_by('-created_at')
    scores = [ form.getEvaluatorPart1Scores() for form in ipcrf_forms ]
            
    # Initialize counters
    promotion_count = 0
    retention_count = 0
    termination_count = 0
    overall_scores = []
    
    # Classify scores
    for score in scores:
        # for _, value in score.items():
        #     average_score = value['Average']
        #     overall_scores.append(average_score)
        #     category = classify_ipcrf_score(average_score if average_score else 0) 
        #     if category == 'Outstanding':
        #         promotion_count += 1
        #     elif category in ['Very Satisfactory', 'Satisfactory']:
        #         retention_count += 1
        #     elif category in ['Unsatisfactory', 'Poor']:
        #         termination_count += 1
        if score is not None:
            average_score = score.get('average_score', 0)
        else :
            average_score = 0 
        overall_scores.append(average_score)
        category = classify_ipcrf_score(average_score if average_score else 0)
        if category == 'Outstanding':
                promotion_count += 1
        elif category in ['Very Satisfactory', 'Satisfactory']:
                retention_count += 1
        elif category in ['Unsatisfactory', 'Poor']:
                termination_count += 1
        
    # Calculate percentages
    total = len(overall_scores)
    promotion_percentage = promotion_count / total * 100 if total > 0 else 0
    retention_percentage = retention_count / total * 100 if total > 0 else 0
    termination_percentage = termination_count / total * 100 if total > 0 else 0

    if promotion_percentage > retention_percentage and promotion_percentage > termination_percentage:
        return 'Promotion'
    elif retention_percentage > termination_percentage:
        return 'Retention'
    else:
        return 'Termination'


def get_kra_breakdown_of_a_teacher(employee_id : str):
    """
        Return dictionary of the RPMSAttachment of the teacher
        breakdown = {
            'kra' : ['KRA1 1', 'KRA 2', 'KRA 3', 'KRA 4', 'PLUS FACTOR' ],
            'averages' : [ 'avg1', 'avg2', 'avg3', 'avg4', 'avg5' ]
        }
    """

    teacher = models.People.objects.filter( is_accepted = True, employee_id=employee_id).first()
    rpms_attachments = models.RPMSAttachment.objects.filter(employee_id=employee_id)
    breakdown = {
        'kra' : [],
        'averages' : []
    }
    for rpms_attachment in rpms_attachments:
        data = rpms_attachment.getGradeSummary()
        breakdown['kra'].append(data['Title'])
        breakdown['averages'].append(data['Average'])
    
    return breakdown


def get_kra_breakdown_of_school(school_id: str):
    """
    Return dictionary of the RPMSAttachment of the school
    breakdown = {
        'kra': ['KRA1', 'KRA2', 'KRA3', 'KRA4', 'PLUS FACTOR'],
        'averages': ['avg1', 'avg2', 'avg3', 'avg4', 'avg5']
    }
    """
    school = models.School.objects.filter(school_id=school_id).first()
    teachers = models.People.objects.filter(is_accepted = True, school_id=school.id)
    breakdown = {
        'kra': [],
        'averages': []
    }
    kra_sums = {}
    kra_counts = {}

    for teacher in teachers:
        rpms_attachments = models.RPMSAttachment.objects.filter(teacher_id=teacher.id)
        for rpms_attachment in rpms_attachments:
            data = rpms_attachment.getGradeSummary()
            kra = data['Title']
            avg = float(data['Average'])
            
            if kra not in kra_sums:
                kra_sums[kra] = 0
                kra_counts[kra] = 0
                
            kra_sums[kra] += avg
            kra_counts[kra] += 1

    for kra in kra_sums.keys():
        breakdown['kra'].append(kra)
        breakdown['averages'].append(kra_sums[kra] / kra_counts[kra])

    return breakdown


def classify_ipcrf_score(score):
    if 4.500 <= score <= 5.000:
        return "Outstanding"
    elif 3.500 <= score < 4.500:
        return "Very Satisfactory"
    elif 2.500 <= score < 3.500:
        return "Satisfactory"
    elif 1.500 <= score < 2.500:
        return "Unsatisfactory"
    elif score < 1.500:
        return "Poor"
    else:
        return "Unknown"


def recommend_rank(teacher : models.People):
    tenure = teacher.working_years()
    current_rank = teacher.position
    recent_form = models.IPCRFForm.objects.filter(employee_id=teacher.employee_id, form_type='PART 1', is_expired=False).order_by('-created_at').first()
    recent_ipcrf_score = recent_form.average_score if recent_form else 0  # Assume this method returns the most recent IPCRF score
    score_classification = classify_ipcrf_score(recent_ipcrf_score)
    
    recommendation = []

    if current_rank == "Teacher I":
        if tenure >= 1:
            recommendation.append("Teacher II")
        if tenure >= 2:
            recommendation.append("Teacher III")
    elif current_rank == "Teacher III":
        if tenure >= 3:
            recommendation.append("Master Teacher I")
    elif current_rank == "Master Teacher I":
        if tenure >= 1:
            recommendation.append("Master Teacher II")
    elif current_rank == "Master Teacher II":
        if score_classification == "Very Satisfactory":
            recommendation.append("Master Teacher III")
    elif current_rank == "Master Teacher III":
        if score_classification == "Outstanding":
            recommendation.append("Master Teacher IV")
    
    return recommendation


def is_proficient_faculty(people : models.People):
    if people.position in position['Proficient']:
        return True
    return False

def is_highly_proficient_faculty(people : models.People):
    if people.position in position['Highly Proficient']:
        return True
    return False


def create_cot_form( 
        school : models.School , 
        evaluator : models.People ,  
        subject : str , 
        cot_date : str, 
        quarter : str, 
        cot_type : str, 
        school_year : str,
        teacher : models.People
    ):
    cot_form = models.COTForm.objects.create(
        school_id = school.school_id,
        employee_id = evaluator.employee_id,
        school_year = school_year,
        evaluated_id = teacher.employee_id,
        quarter = quarter
    )
    
    cot_form.cot_form_id = str(uuid4())
    
    content = {
            "COT Type" : f"{cot_type}",
            "Observer ID" : f"{evaluator.employee_id}",
            "Observer Name" : f"{evaluator.fullname}",
            "Teacher Name" : f"{teacher.fullname}",
            "Teacher ID" : f"{teacher.employee_id}",
            "Subject & Grade Level" : f"{subject}",
            "Date" : f"{cot_date}",
            "Quarter": f"{quarter}",
            "Comments" : ""
        }

    if cot_type == 'Highly Proficient':
        content["Questions"] = forms_text.form_cot_highly_proficient()
    elif cot_type == 'Proficient':
        content["Questions"] = forms_text.form_cot_proficient()
    
    cot_form.content = content
    cot_form.is_for_teacher_proficient = True if cot_type == 'Proficient' else False
    cot_form.save()
    return cot_form


def update_cot_form(cot_form : models.COTForm, comment : str , questions : dict[str, dict] , content : dict[str, dict] ):
    # cot_form.content['Comments'] = comment
    # for q_id, q_info in questions.items():
    #     cot_form.content['Questions'][q_id]['Selected'] = q_info['Selected'] 
    cot_form.content = content
    cot_form.is_checked = True
    cot_form.save()



def create_ipcrf_form_proficient( school : models.School , teacher : models.People , school_year : str):
    # Currently walang evaluator
    
    connection_to_other = str(uuid4())
    
    # Create part 1
    ipcrf_form_part_1 = models.IPCRFForm.objects.create(
        school_id = school.school_id,
        employee_id = teacher.employee_id,
        form_type = 'PART 1',
        school_year = school_year,
        is_for_teacher_proficient = True
    )
    
    
    ipcrf_form_part_1.content_for_teacher = forms_text.form_for_ipcrf_part_1_proficient()
    ipcrf_form_part_1.content_for_evaluator = forms_text.form_for_ipcrf_part_1_proficient()
    ipcrf_form_part_1.connection_to_other = connection_to_other
    ipcrf_form_part_1.save()

    # Create part 2
    ipcrf_form_part_2 = models.IPCRFForm.objects.create(
        school_id = school.school_id,
        employee_id = teacher.employee_id,
        form_type = 'PART 2',
        school_year = school_year,
        is_for_teacher_proficient = True
    )
    
    ipcrf_form_part_2.content_for_teacher = forms_text.form_for_ipcrf_part_2_proficient()
    ipcrf_form_part_2.connection_to_other = connection_to_other
    ipcrf_form_part_2.save()
    
    # Create part 3
    ipcrf_form_part_3 = models.IPCRFForm.objects.create(
        school_id = school.school_id,
        employee_id = teacher.employee_id,
        form_type = 'PART 3',
        school_year = school_year,
        is_for_teacher_proficient = True
    )
    
    
    ipcrf_form_part_3.content_for_teacher = forms_text.form_for_ipcrf_part_3_proficient()
    ipcrf_form_part_3.connection_to_other = connection_to_other
    ipcrf_form_part_3.save()
    
    return (ipcrf_form_part_1, ipcrf_form_part_2, ipcrf_form_part_3)
    


def create_ipcrf_form_highly_proficient(school : models.School , teacher : models.People ):
     # Currently walang evaluator
    
    connection_to_other = str(uuid4())
    
    # Create part 1
    ipcrf_form_part_1 = models.IPCRFForm.objects.create(
        school_id = school.school_id,
        employee_id = teacher.employee_id,
        form_type = 'PART 1',
    )
    
    
    ipcrf_form_part_1.content_for_teacher = forms_text.form_for_ipcrf_part_1_highly_proficient()
    ipcrf_form_part_1.content_for_evaluator = forms_text.form_for_ipcrf_part_1_highly_proficient()
    ipcrf_form_part_1.connection_to_other = connection_to_other
    ipcrf_form_part_1.save()

    # Create part 2 THEY ARE SO NO NEED TO CHANGE FORM
    ipcrf_form_part_2 = models.IPCRFForm.objects.create(
        school_id = school.school_id,
        employee_id = teacher.employee_id,
        form_type = 'PART 2',
    )
    
    ipcrf_form_part_2.content_for_teacher = forms_text.form_for_ipcrf_part_2_proficient()
    ipcrf_form_part_2.connection_to_other = connection_to_other
    ipcrf_form_part_2.save()
    
    # Create part 3 THEY ARE SO NO NEED TO CHANGE FORM
    ipcrf_form_part_3 = models.IPCRFForm.objects.create(
        school_id = school.school_id,
        employee_id = teacher.employee_id,
        form_type = 'PART 3',
    )
    
    
    ipcrf_form_part_3.content_for_teacher = forms_text.form_for_ipcrf_part_3_proficient()
    ipcrf_form_part_3.connection_to_other = connection_to_other
    ipcrf_form_part_3.save()
    
    return (ipcrf_form_part_1, ipcrf_form_part_2, ipcrf_form_part_3)
    



def update_ipcrf_form_part_1_by_evaluator(
    ipcrf_form : models.IPCRFForm,
    content : dict[str, dict]
    ):
    
    ipcrf_form.content_for_teacher = content
    ipcrf_form.is_checked_by_evaluator = True
    ipcrf_form.save()


def update_iprcf_form_part_1_by_teacher(
    ipcrf_form : models.IPCRFForm,
    content : dict[str, dict]
    ):
    
    part_3 = models.IPCRFForm.objects.filter(connection_to_other=ipcrf_form.connection_to_other, form_type='PART 3').order_by('-created_at').first()
    # TODO : UPDATE THE CONTENT OF PART 3
    Str = []
    Dev = []

    for domain, questions in content.items():
        for q_id, q_info in questions.items():
            all_five = True
            for key, value in q_info.items():
                if key in ['QUALITY', 'EFFICIENCY', 'TIMELINES'] and value.get('Rate') != '5':
                    all_five = False
            if all_five:
                Str.append(q_info['Question'])
            else:
                Dev.append(q_info['Question'])
    
    part_3.content_for_teacher['A'][0]['Strenghts'] = Str
    part_3.content_for_teacher['A'][0]['Development Needs'] = Dev
    
    part_3.save()
    
    ipcrf_form.content_for_teacher = content 
    ipcrf_form.save()


def update_ipcrf_form_part_2_by_teacher(
    ipcrf_form : models.IPCRFForm,
    content : dict[str, dict]
    ):
    
    part_3 = models.IPCRFForm.objects.filter(connection_to_other=ipcrf_form.connection_to_other, form_type='PART 3').order_by('-created_at').first()
    
    Yes = []
    No = []
    
    # Iterate over self-management data
    for key, value in content.items():
        if len(value["Selected"]) > 1:
            Yes.append(value["Title"])
        else:
            No.append(value["Title"])
    
    part_3.content_for_teacher['B']['Strenghts'] = Yes
    part_3.content_for_teacher['B']['Development Needs'] = No
    
    part_3.save()
    
    
    ipcrf_form.content_for_teacher = content
    ipcrf_form.save()


def update_ipcrf_form_part_3_by_teacher(
    ipcrf_form : models.IPCRFForm,
    content : dict[str, dict]
    ):
    
    ipcrf_form.content_for_teacher = content
    
    ipcrf_form.is_checked = True
    ipcrf_form.save()
    
    
    part_1 = models.IPCRFForm.objects.filter(connection_to_other=ipcrf_form.connection_to_other, form_type='PART 1').order_by('-created_at').first()
    part_1.is_checked = True
    part_1.save()
    
    part_2 = models.IPCRFForm.objects.filter(connection_to_other=ipcrf_form.connection_to_other, form_type='PART 2').order_by('-created_at').first()
    part_2.is_checked = True
    part_2.save()



# TODO : UPDATE THE CONTENT OF THE RPMS CLASS WORKS HERE  
def create_rpms_class_works_for_proficient(rpms_folder_id : str):
    # Create KRA 1
    kra_1 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 1: Content Knowledge and Pedagogy',
    )
    kra_1.class_work_id = str(uuid4())
    
    kra_1.objectives = forms_text.form_for_kra1_proficient()
    
    kra_1.save()
    
    # Create KRA 2
    kra_2 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 2: Learning Environment and Diversity of Learners',
    )
    kra_2.class_work_id = str(uuid4())
    
    kra_2.objectives = forms_text.form_for_kra2_proficient()
    
    kra_2.save()
    
    
    # Create KRA 3
    kra_3 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 3: Curriculum and Planning',
    )
    
    kra_3.class_work_id = str(uuid4())
    kra_3.objectives = forms_text.form_for_kra3_proficient()
    
    kra_3.save()
    
    
    
    # Create KRA 4
    kra_4 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 4:  Curriculum and Planning & Assessment and Reporting',
    )
    
    kra_4.class_work_id = str(uuid4())
    
    kra_4.objectives = forms_text.form_for_kra4_proficient()
    
    kra_4.save()
    
    # Create PLUS FACTOR
    plus_factor = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'PLUS FACTOR',
    )
    
    plus_factor.class_work_id = str(uuid4())
    
    plus_factor.objectives = forms_text.form_for_plus_factor_proficient()
    
    plus_factor.save()
    
  
def create_rpms_class_works_for_highly_proficient(rpms_folder_id : str):
    # Create KRA 1
    kra_1 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 1: Content Knowledge and Pedagogy',
    )
    kra_1.class_work_id = str(uuid4())
    
    kra_1.objectives = forms_text.form_for_kra1_highly_proficient()
    
    kra_1.save()
    
    # Create KRA 2
    kra_2 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 2: Learning Environment and Diversity of Learners',
    )
    kra_2.class_work_id = str(uuid4())
    
    kra_2.objectives = forms_text.form_for_kra2_highly_proficient()
    
    kra_2.save()
    
    
    # Create KRA 3
    kra_3 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 3: Curriculum and Planning',
    )
    
    kra_3.class_work_id = str(uuid4())
    kra_3.objectives = forms_text.form_for_kra3_highly_proficient()
    
    kra_3.save()
    
    
    
    # Create KRA 4
    kra_4 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 4:  Curriculum and Planning & Assessment and Reporting',
    )
    
    kra_4.class_work_id = str(uuid4())
    
    kra_4.objectives = forms_text.form_for_kra4_highly_proficient()
    
    kra_4.save()
    
    # Create PLUS FACTOR
    plus_factor = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'PLUS FACTOR',
    )
    
    plus_factor.class_work_id = str(uuid4())
    
    plus_factor.objectives = forms_text.form_for_plus_factor_highly_proficient()
    
    plus_factor.save()


def update_rpms_attachment( rpms_attachment : models.RPMSAttachment, content : dict):
    rpms_attachment.grade = content
    rpms_attachment.is_checked = True
    rpms_attachment.save()
    
    

def calculate_scores_for_proficient(domains : dict , cot_content : dict):
    # Initialize variables
    efficiency_scores = []
    quality_scores = []
    timeliness_scores = []
    total_kra_score = 0
    
    # Extract and calculate the scores
    for category, objectives in domains.items():
        for obj_id, details in objectives.items():
            question = details.get('Question', '')
            quality = int(details.get('QUALITY', {}).get('Rate', 0))
            efficiency = int(details.get('EFFICIENCY', {}).get('Rate', 0))
            timeliness = int(details.get('TIMELINES', {}).get('Rate', 0))
            
            # Collect scores for KRA calculation
            if category != 'PLUS FACTOR':
                efficiency_scores.append(efficiency)
                quality_scores.append(quality)
                timeliness_scores.append(timeliness)
            # Add Plus Factor separately
            else:
                total_kra_score += (quality + efficiency + timeliness)
    
    # Extract COTFORM Question Content
    questions = cot_content.get('Questions', {})
    question_selected = {}
    for q_id, q_info in questions.items():
        question_selected[q_id] = int(q_info['Selected']) if q_info['Selected'] != '0' else 3
    
    # Calculate total KRA score
    # total_kra_score += (
    #     ((efficiency_scores[0] + quality_scores[0]) / 2) * 0.07 +
    #     ((efficiency_scores[1] + quality_scores[1]) / 2) * 0.07 +
    #     ((efficiency_scores[2] + quality_scores[2]) / 2) * 0.07 +
    #     ((efficiency_scores[3] + quality_scores[3]) / 2) * 0.07 +
    #     ((efficiency_scores[4] + quality_scores[4]) / 2) * 0.07 +
    #     ((efficiency_scores[5] + quality_scores[5]) / 2) * 0.07 +
    #     ((efficiency_scores[6] + quality_scores[6]) / 2) * 0.07 +
    #     ((efficiency_scores[7] + quality_scores[7]) / 2) * 0.07 +
    #     ((quality_scores[8] + efficiency_scores[8]) / 2) * 0.07 +
    #     ((efficiency_scores[9] + quality_scores[3]) / 2) * 0.07 +
    #     ((quality_scores[10] + timeliness_scores[10]) / 2) * 0.07 +
    #     ((quality_scores[11] + timeliness_scores[11]) / 2) * 0.07 +
    #     ((quality_scores[12] + timeliness_scores[12]) / 2) * 0.07 +
    #     ((efficiency_scores[13] + quality_scores[13] + timeliness_scores[13]) / 3) * 0.07
    # )
    
    totalKraScore = (
        ((efficiency_scores[0] + (question_selected['1'] / 7) ) / 2) * 0.07 + 
        ((efficiency_scores[1] + (question_selected['2'] / 7)) / 2) * 0.07 +
        ((efficiency_scores[2] + (question_selected['3'] / 7)) / 2) * 0.07 +
        ((efficiency_scores[3] + (question_selected['4'] / 7)) / 2) * 0.07 +
        ((efficiency_scores[4] + (question_selected['5'] / 7)) / 2 ) * 0.07 +
        ((efficiency_scores[5] + (question_selected['6'] / 7)) / 2) * 0.07 +
        ((efficiency_scores[6] + (question_selected['7'] / 7)) / 2) * 0.07 +
        ((efficiency_scores[7] + (question_selected['8'] / 7)) / 2) * 0.07 +
        ((quality_scores[8] + efficiency_scores[8]) / 2) * 0.07 +
        ((efficiency_scores[9] + (question_selected['4'] / 7)) / 2) * 0.07 +
        ((quality_scores[10] + timeliness_scores[10]) / 2) * 0.07 +
        ((quality_scores[11] + timeliness_scores[11]) / 2) * 0.07 +
        ((quality_scores[12] + timeliness_scores[12]) / 2) * 0.07 +
        ((efficiency_scores[13] + quality_scores[13] + timeliness_scores[13]) / 3) * 0.07
    )
    
    # Calculate Plus Factor score
    plus_factor_score = sum(
        int(details.get('QUALITY', {}).get('Rate', 0)) + 
        int(details.get('EFFICIENCY', {}).get('Rate', 0)) + 
        int(details.get('TIMELINES', {}).get('Rate', 0)) 
        for details in domains.get('PLUS FACTOR', {}).values()
    )
    plus_factor = (plus_factor_score / 3) * 0.02

    # Calculate final total score
    total_score = total_kra_score + plus_factor

    # Print the results
    # Total KRA Score:  1.085
    # Plus Factor:  0.09333333333333334
    # Total Score:  1.1783333333333335

    
    return {
        'total_kra_score' : total_kra_score,
        'plus_factor' : plus_factor,
        'total_score' : total_score
    }



def calculate_scores_for_highly_proficient(domains : dict , cot_content : dict):
    efficiency_scores = []
    quality_scores = []
    timeliness_scores = []
    total_kra_score = 0

    for category, objectives in domains.items():
        for obj_id, details in objectives.items():
            quality = int(details.get('QUALITY', {}).get('Rate', 0))
            efficiency = int(details.get('EFFICIENCY', {}).get('Rate', 0))
            timeliness = int(details.get('TIMELINESS', {}).get('Rate', 0))

            efficiency_scores.append(efficiency)
            quality_scores.append(quality)
            timeliness_scores.append(timeliness)
            
            

    # Extract COTFORM Question Content
    questions = cot_content.get('Questions', {})
    question_selected = {}
    for q_id, q_info in questions.items():
        question_selected[q_id] = int(q_info['Selected']) if q_info['Selected'] != '0' else 3
        

    total_kra_score = (
            ((efficiency_scores[0] + (question_selected['1'] / 7)) / 2) * 0.07 +
            ((quality_scores[1] + timeliness_scores[1]) / 2) * 0.07 +
            ((efficiency_scores[2] + (question_selected['3'] / 7)) / 2) * 0.07 +
            ((efficiency_scores[3] + (question_selected['4'] / 7)) / 2) * 0.07 +
            ((efficiency_scores[4] + (question_selected['5'] / 7)) / 2) * 0.07 +
            ((efficiency_scores[5] + (question_selected['6'] / 7)) / 2) * 0.07 +
            ((efficiency_scores[6] + (question_selected['7'] / 7)) / 2) * 0.07 +
            ((quality_scores[7] + (question_selected['8'] / 7)) / 2) * 0.07 +
            ((quality_scores[8] + timeliness_scores[8]) / 2) * 0.07 +
            ((efficiency_scores[9] + (question_selected['9'] / 7)) / 2) * 0.07 +
            ((quality_scores[10] + timeliness_scores[10]) / 2) * 0.07 +
            ((quality_scores[11] + timeliness_scores[11]) / 2) * 0.07 +
            ((quality_scores[12] + timeliness_scores[12]) / 2) * 0.07 +
            ((efficiency_scores[13] + quality_scores[13]) / 2) * 0.07
        )


    plus_factor_score = sum(
        int(details.get('QUALITY', {}).get('Rate', 0)) +
        int(details.get('EFFICIENCY', {}).get('Rate', 0)) +
        int(details.get('TIMELINESS', {}).get('Rate', 0))
        for details in domains.get('PLUS FACTOR', {}).values()
    )
    plus_factor = (plus_factor_score / 3) * 0.02

    total_score = total_kra_score + plus_factor

    
    # Total KRA Score:  1.085
    # Plus Factor:  0.09333333333333334
    # Total Score:  1.1783333333333335

    return {
        'total_kra_score': total_kra_score,
        'plus_factor': plus_factor,
        'total_score': total_score
    }



def calculate_scores(domains, cot_content, employee_position):
    # Determine if the employee is Proficient or Highly Proficient
    positions = {
        'Proficient': ('Teacher I', 'Teacher II', 'Teacher III'),
        'Highly Proficient': ('Master Teacher I', 'Master Teacher II', 'Master Teacher III', 'Master Teacher IV')
    }

    if employee_position in positions['Proficient']:
        return calculate_scores_for_proficient(domains, cot_content)
    elif employee_position in positions['Highly Proficient']:
        return calculate_scores_for_highly_proficient(domains, cot_content)

def get_employee_performance_by_year(employee_id, employee_position):
    # Initialize the result dictionary
    performance_by_year = defaultdict(lambda: {"ipcrf": [], "cot": []})

    # Query IPCRF forms filtered by employee_id and annotate with year
    ipcrf_forms = models.IPCRFForm.objects.filter(employee_id=employee_id , form_type='PART 1').annotate(year=ExtractYear('created_at'))
    for form in ipcrf_forms:
        performance_by_year[form.year]["ipcrf"].append(form)

    # Query COT forms filtered by employee_id and annotate with year
    cot_forms = models.COTForm.objects.filter(evaluated_id=employee_id).annotate(year=ExtractYear('created_at'))
    for form in cot_forms:
        performance_by_year[form.year]["cot"].append(form)
        
    # Calculate scores for each year
    results = {}
    for year, forms in performance_by_year.items():
        domains = {}  # Merge or prepare domains data here as needed
        cot_content = {}  # Prepare COT content here as needed
        results[year] = calculate_scores(domains, cot_content, employee_position)
    
    # {
    #     2021: {
    #         'total_kra_score': 1.85,
    #         'plus_factor': 0.02,
    #         'total_score': 1.87
    #     },
    #     2022: {
    #         'total_kra_score': 2.40,
    #         'plus_factor': 0.04,
    #         'total_score': 2.44
    #     },
    #     2023: {
    #         'total_kra_score': 2.10,
    #         'plus_factor': 0.03,
    #         'total_score': 2.13
    #     }
    # }
    
    return results




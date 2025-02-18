from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.templatetags.static import static
from django.db.models.functions import ExtractYear
from django.utils import timezone
from django.conf import settings
from django.templatetags.static import static
import time

import io
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle



from collections import defaultdict

from datetime import datetime

# Import requests first
import requests
from curl_cffi import requests as cf_reqs  # Import curl_cffi after requests


from g4f.client import Client
from uuid import uuid4
from . import models, forms_text
from django.db.models import Count

import json
import time
import logging







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


def is_proficient_faculty(people : models.People , is_faculty = False):
    if is_faculty:
        return people.position in evaluator_positions['Proficient']
    
    if people.position in position['Proficient']:
        return True
    return False

def is_highly_proficient_faculty(people : models.People, is_faculty = False):
    if is_faculty:
        return people.position in evaluator_positions['Highly Proficient']
    
    if people.position in position['Highly Proficient']:
        return True
    return False



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
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": promt}],
        )
        return str(response.choices[0].message.content)
    except Exception as e:
        return str(e)
 


def exponential_backoff(attempt, base=2):
    return base ** attempt

import json
import time
import logging
import random
import re

def exponential_backoff(attempt, base=2, max_backoff=60):
    return min(base ** attempt + random.uniform(0, 1), max_backoff)

def extract_json(text):
    dict_pattern = re.compile(r'\{.*?\}', re.DOTALL)
    match = dict_pattern.search(text)
    if match:
        return match.group(0)
    return None

def generate_text_v2(prompt: str):
    max_retries = 10  # Increase retries if needed
    attempt_info = []

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
            )
            # Log the raw response for debugging
            raw_result = str(response.choices[0].message.content)
            logging.debug(f"Raw API Response: {raw_result}")

            if not raw_result.strip():
                raise ValueError("Empty response received from API")

            json_text = extract_json(raw_result)  # Extract the dictionary part
            if json_text:
                try:
                    result_json: dict = json.loads(json_text)
                    return result_json
                except json.JSONDecodeError as e:
                    logging.warning(f"JSON decode error: {e}. Returning raw string.")
                    return {'error': f"JSONDecodeError: {e}", 'raw_response': raw_result}
            else:
                return {'raw_response': raw_result}

        except Exception as e:
            error_message = str(e)
            attempt_info.append({'attempt': attempt + 1, 'error': error_message})

            if "Too Many Requests" in error_message or "Rate limit reached" in error_message:
                wait_time = exponential_backoff(attempt)
                logging.warning(f"Rate limit reached, retrying in {wait_time:.2f} seconds... (Attempt {attempt + 1})")
                time.sleep(wait_time)
            else:
                logging.error(f"Error during API call: {error_message}")
                return {'error': error_message, 'details': attempt_info}
    
    logging.error(f"Failed to generate text after {max_retries} attempts. Details: {attempt_info}")
    return {'error': "Failed to generate text after multiple attempts.", 'details': attempt_info}

# # Example usage
# data = {
#     'strengths': 'What are the strengths?',
#     'weaknesses': 'What are the weaknesses?',
#     'opportunities': 'What are the opportunities?',
#     'threats': 'What are the threats?'
# }

# strength = generate_text_v2(data['strengths'])
# weakness = generate_text_v2(data['weaknesses'])
# opportunity = generate_text_v2(data['opportunities'])
# threat = generate_text_v2(data['threats'])

# print(strength)
# print(weakness)
# print(opportunity)
# print(threat)


def send_verification_email(user_email, verification_code , template , masbate_locker_email , subject, request):
    subject = subject 
    from_email = masbate_locker_email
    to_email = user_email
 
    deped_logo_url = request.build_absolute_uri(static('logo.png'))
    # Render the HTML template 
    html_content = render_to_string(template, {
        'verification_code': verification_code ,
        'deped_logo' : deped_logo_url,
        'verification_for' : subject
    })
    text_content = strip_tags(html_content)  # Create a plain text version

    # Create the email
    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    email.attach_alternative(html_content, "text/html")
    initial_delay=5
    while True:
        try:
            email.send()
            print("Email Sent Successfully")
            break
        except Exception as e:
            time.sleep(1000)
            time.sleep(initial_delay)
            initial_delay *= 2  # Exponential backoff


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
    initial_delay=5
    while True:
        try:
            email.send()
            print("Email Sent Successfully")
            break
        except Exception as e:
            time.sleep(1000)
            time.sleep(initial_delay)
            initial_delay *= 2  # Exponential backoff




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
    initial_delay=5
    while True:
        try:
            email.send()
            print("Email Sent Successfully")
            break
        except Exception as e:
            time.sleep(1000)
            time.sleep(initial_delay)
            initial_delay *= 2  # Exponential backoff



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
    initial_delay=5
    while True:
        try:
            email.send()
            print("Email Sent Successfully")
            break
        except Exception as e:
            time.sleep(1000)
            time.sleep(initial_delay)
            initial_delay *= 2  # Exponential backoff


def parse_date_string(date_string):
    try:
        naive_datetime = datetime.strptime(date_string, "%B %d, %Y")
        parsed_date = timezone.make_aware(naive_datetime, timezone.get_current_timezone())
        return parsed_date
    except ValueError:
        print(f"Error: The date format of '{date_string}' is incorrect.")
        return None


def get_ipcrf_forms_by_years(employee_id : str ):  

    # Group by year
    ipcrf_forms_by_year = models.IPCRFForm.objects.filter(
        employee_id=employee_id, form_type='PART 1'
    ).annotate(
        year=ExtractYear('created_at')
    ).order_by('created_at')

    # Initialize the dictionary with a default list
    ipcrf_yearly_dict = defaultdict(list)

    # Populate the dictionary
    for index, entry in enumerate(ipcrf_forms_by_year):
        year_label = f'Year {index + 1}'
        ipcrf_yearly_dict[year_label].append(entry)

    # Convert defaultdict to regular dict
    ipcrf_yearly_dict = dict(ipcrf_yearly_dict)

    # Example dictionary structure
    # {
    #     'Year 1': [<IPCRFForm: IPCRFForm object (1)>, <IPCRFForm: IPCRFForm object (2)>],
    #     'Year 2': [<IPCRFForm: IPCRFForm object (3)>, <IPCRFForm: IPCRFForm object (4)>],
    #     ...
    # }

    return ipcrf_yearly_dict


def get_rpms_forms_by_title(employee_id : str , school_year = None):
    
    # Filter and group by title
    
    titles = {
        "PLUS FACTOR" : "Plus Factor",
        "KRA 4:  Curriculum and Planning & Assessment and Reporting" : "KRA 4",
        "KRA 3: Curriculum and Planning" : "KRA 3",
        "KRA 2: Learning Environment and Diversity of Learners" : "KRA 2",
        "KRA 1: Content Knowledge and Pedagogy" : "KRA 1",
    }
    
    # Create the dictionary
    result_dict = {
        "KRA 1" : [0],
        "KRA 2" : [0],
        "KRA 3" : [0],
        "KRA 4" : [0],
        "Plus Factor" : [0],
    }
    
    teacher = models.People.objects.filter(is_deactivated = False, employee_id = employee_id).first()
    
    if school_year :
        attachments = models.RPMSAttachment.objects.filter(employee_id=teacher.employee_id, school_id=teacher.school_id , school_year=school_year).order_by("-created_at")
        
    else :
        attachments = models.RPMSAttachment.objects.filter(employee_id=teacher.employee_id, school_id=teacher.school_id).order_by("-created_at")
    
    for attachment in attachments:
        title = attachment.title
        if title in titles:
            title = titles[title]
            score = attachment.getGradeSummary().get('Total', 0)
            result_dict[title].append(score)

    
    return result_dict
    


def get_performance_by_years( employee_id : str):
    forms = get_ipcrf_forms_by_years(employee_id)
    data = {
        "labels" : [],
        "values" : []
    }
    
    for year, forms in forms.items():
        data["labels"].append(year)
        value = 0.0
        for form in forms:
            value += form.evaluator_rating
        data["values"].append((value / len(forms)) if len(forms) > 0 else 0.0)
    return data



def get_recommendation_result(employee_id : str):
    ipcrf_forms = models.IPCRFForm.objects.filter(employee_id=employee_id, form_type='PART 1').order_by('-created_at')
    scores = [ form.evaluator_rating for form in ipcrf_forms ]
            
    # Initialize counters
    promotion_count = 0
    retention_count = 0
    termination_count = 0
    overall_scores = []
    
    # Classify scores
    for score in scores: 
        overall_scores.append(score)
        category = classify_ipcrf_score(score)
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



def get_recommendation_result_with_percentage(employee_id : str):
    ipcrf_forms = models.IPCRFForm.objects.filter(employee_id=employee_id, form_type='PART 1').order_by('-created_at')
    scores = [ form.evaluator_rating for form in ipcrf_forms ]
            
    # Initialize counters
    promotion_count = 0
    retention_count = 0
    termination_count = 0
    overall_scores = []
    
    # Classify scores
    for score in scores: 
        overall_scores.append(score)
        category = classify_ipcrf_score(score)
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

    result = {
        "result" : "",
        'promotion_percentage' : promotion_percentage,
        'retention_percentage' : retention_percentage,
        'termination_percentage' : termination_percentage
    }
    if promotion_percentage > retention_percentage and promotion_percentage > termination_percentage:
        result["result"] = 'Promotion'
    elif retention_percentage > termination_percentage:
        result["result"] = 'Retention'
    else:
        result["result"] = 'Termination'
    
    return result


def get_kra_breakdown_of_a_teacher(employee_id : str , school_year = None):
    """
        Return dictionary of the RPMSAttachment of the teacher
        breakdown = {
            'kra' : ['KRA1 1', 'KRA 2', 'KRA 3', 'KRA 4', 'PLUS FACTOR' ],
            'averages' : [ 'avg1', 'avg2', 'avg3', 'avg4', 'avg5' ]
        }
    """

    breakdown = {
        'kra' : [],
        'averages' : [],
        'scores' : []
    }
    
    results = get_rpms_forms_by_title(employee_id , school_year)
    
    total_score = 0.0
    real_total_score = 0
    for kra, scores in results.items():
        breakdown['kra'].append(kra)
        breakdown['scores'].append(sum(scores))
        real_total_score = real_total_score + (sum(scores) if len(scores) > 0 else 0)
        total_score = total_score + (sum(scores) / len(scores) if len(scores) > 0 else 0)
        breakdown['averages'].append(sum(scores) / len(scores) if len(scores) > 0 else 0)
    
    breakdown['averages'].append(total_score)
    breakdown['kra'].append("Total Score")
    breakdown['scores'].append(real_total_score)
    
    
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
    teachers = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=school.id)
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


def recommend_rank(teacher : models.People , school_year = None):
    tenure = teacher.working_years()
    current_rank = teacher.position
    
    if school_year: 
        recent_form = models.IPCRFForm.objects.filter(employee_id=teacher.employee_id, form_type='PART 1', school_year=school_year).order_by('-created_at').first()
    else:
        recent_form = models.IPCRFForm.objects.filter(employee_id=teacher.employee_id, form_type='PART 1').order_by('-created_at').first()
    
    recent_ipcrf_score = recent_form.evaluator_rating if recent_form else 0  # Assume this method returns the most recent IPCRF score
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
        employee_id = evaluator.employee_id if evaluator else "",
        school_year = school_year,
        evaluated_id = teacher.employee_id,
        quarter = quarter
    )
    
    cot_form.cot_form_id = str(uuid4())
    
    content = {
            "COT Type" : f"{cot_type}",
            "Observer ID" : f"{evaluator.employee_id if evaluator else ''}",
            "Observer Name" : f"{evaluator.fullname if evaluator else ''}",
            "Teacher Name" : f"{teacher.fullname}",
            "Teacher ID" : f"{teacher.employee_id}",
            "Subject & Grade Level" : f"{subject}",
            "Date" : f"{cot_date}",
            "Quarter": f"{quarter}",
            "Comments" : "",
            "Questions" : {}
        }

    if cot_type == 'Highly Proficient':
        content["Questions"] = forms_text.form_cot_highly_proficient()
    elif cot_type == 'Proficient':
        content["Questions"] = forms_text.form_cot_proficient()
    
    cot_form.content = content
    cot_form.is_for_teacher_proficient = True if cot_type == 'Proficient' else False
    cot_form.save()
    
    
    
    models.LastFormCreated.objects.create(
        school_id = school.school_id,
        form_type = "COT",
        form_id = cot_form.cot_form_id,
        is_for_teacher_proficient = cot_form.is_for_teacher_proficient,
        school_year = school_year
    )
    
    
    
    
    
    
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
    
    
    models.LastFormCreated.objects.create(
        school_id = school.school_id,
        form_type = "IPCRF",
        form_id = ipcrf_form_part_1.connection_to_other,
        is_for_teacher_proficient = True,
        school_year = school_year
    )
    
    return (ipcrf_form_part_1, ipcrf_form_part_2, ipcrf_form_part_3)
    


def create_ipcrf_form_highly_proficient(school : models.School , teacher : models.People, school_year : str ):
     # Currently walang evaluator
    
    connection_to_other = str(uuid4())
    
    # Create part 1
    ipcrf_form_part_1 = models.IPCRFForm.objects.create(
        school_id = school.school_id,
        employee_id = teacher.employee_id,
        form_type = 'PART 1',
        school_year = school_year,
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
        school_year = school_year,
    )
    
    ipcrf_form_part_2.content_for_teacher = forms_text.form_for_ipcrf_part_2_proficient()
    ipcrf_form_part_2.connection_to_other = connection_to_other
    ipcrf_form_part_2.save()
    
    # Create part 3 THEY ARE SO NO NEED TO CHANGE FORM
    ipcrf_form_part_3 = models.IPCRFForm.objects.create(
        school_id = school.school_id,
        employee_id = teacher.employee_id,
        form_type = 'PART 3',
        school_year = school_year,
    )
    
    
    ipcrf_form_part_3.content_for_teacher = forms_text.form_for_ipcrf_part_3_proficient()
    ipcrf_form_part_3.connection_to_other = connection_to_other
    ipcrf_form_part_3.save()
    
    models.LastFormCreated.objects.create(
        school_id = school.school_id,
        form_type = "IPCRF",
        form_id = ipcrf_form_part_1.connection_to_other,
        is_for_teacher_proficient = False,
        school_year = school_year
    )
    
    return (ipcrf_form_part_1, ipcrf_form_part_2, ipcrf_form_part_3)
    



def update_ipcrf_form_part_1_by_evaluator(
    ipcrf_form : models.IPCRFForm,
    content : dict[str, dict]
    ):
    
    ipcrf_form.content_for_evaluator = content
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
    
    ipcrf_form.is_submitted = True
    ipcrf_form.is_checked = True
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
    
    
    ipcrf_form.is_submitted = True
    ipcrf_form.is_checked = True
    ipcrf_form.content_for_teacher = content
    ipcrf_form.save()


def update_ipcrf_form_part_3_by_teacher(
    ipcrf_form : models.IPCRFForm,
    content : dict[str, dict]
    ):
    
    ipcrf_form.content_for_teacher = content
    
    ipcrf_form.is_submitted = True
    ipcrf_form.is_checked = True
    ipcrf_form.save()
    
    
    # part_1 = models.IPCRFForm.objects.filter(connection_to_other=ipcrf_form.connection_to_other, form_type='PART 1').order_by('-created_at').first()
    # part_1.is_checked = True
    # part_1.save()
    
    # part_2 = models.IPCRFForm.objects.filter(connection_to_other=ipcrf_form.connection_to_other, form_type='PART 2').order_by('-created_at').first()
    # part_2.is_checked = True
    # part_2.save()



# TODO : UPDATE THE CONTENT OF THE RPMS CLASS WORKS HERE  
def create_rpms_class_works_for_proficient(rpms_folder_id : str , school_id : str , rpms_folder_school_year : str):
    # Create KRA 1
    kra_1 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 1: Content Knowledge and Pedagogy',
        school_id=school_id,
        school_year=rpms_folder_school_year
    )
    kra_1.class_work_id = str(uuid4())
    
    kra_1.objectives = forms_text.form_for_kra1_proficient()
    
    kra_1.save()
    
    # Create KRA 2
    kra_2 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 2: Learning Environment and Diversity of Learners',
        school_id=school_id,
        school_year=rpms_folder_school_year
    )
    kra_2.class_work_id = str(uuid4())
    
    kra_2.objectives = forms_text.form_for_kra2_proficient()
    
    kra_2.save()
    
    
    # Create KRA 3
    kra_3 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 3: Curriculum and Planning',
        school_id=school_id,
        school_year=rpms_folder_school_year
    )
    
    kra_3.class_work_id = str(uuid4())
    kra_3.objectives = forms_text.form_for_kra3_proficient()
    
    kra_3.save()
    
    
    
    # Create KRA 4
    kra_4 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 4:  Curriculum and Planning & Assessment and Reporting',
        school_id=school_id
    )
    
    kra_4.class_work_id = str(uuid4())
    
    kra_4.objectives = forms_text.form_for_kra4_proficient()
    
    kra_4.save()
    
    # Create PLUS FACTOR
    plus_factor = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'PLUS FACTOR',
        school_id=school_id,
        school_year=rpms_folder_school_year
    )
    
    plus_factor.class_work_id = str(uuid4())
    
    plus_factor.objectives = forms_text.form_for_plus_factor_proficient()
    
    plus_factor.save()
    
  
def create_rpms_class_works_for_highly_proficient(rpms_folder_id : str, school_id : str , rpms_folder_school_year : str):
    # Create KRA 1
    kra_1 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 1: Content Knowledge and Pedagogy',
        school_id=school_id,
        school_year=rpms_folder_school_year
    )
    kra_1.class_work_id = str(uuid4())
    
    kra_1.objectives = forms_text.form_for_kra1_highly_proficient()
    
    kra_1.save()
    
    # Create KRA 2
    kra_2 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 2: Learning Environment and Diversity of Learners',
        school_id=school_id,
        school_year=rpms_folder_school_year
    )
    kra_2.class_work_id = str(uuid4())
    
    kra_2.objectives = forms_text.form_for_kra2_highly_proficient()
    
    kra_2.save()
    
    
    # Create KRA 3
    kra_3 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 3: Curriculum and Planning',
        school_id=school_id,
        school_year=rpms_folder_school_year
    )
    
    kra_3.class_work_id = str(uuid4())
    kra_3.objectives = forms_text.form_for_kra3_highly_proficient()
    
    kra_3.save()
    
    
    
    # Create KRA 4
    kra_4 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 4:  Curriculum and Planning & Assessment and Reporting',
        school_id=school_id,
        school_year=rpms_folder_school_year
    )
    
    kra_4.class_work_id = str(uuid4())
    
    kra_4.objectives = forms_text.form_for_kra4_highly_proficient()
    
    kra_4.save()
    
    # Create PLUS FACTOR
    plus_factor = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'PLUS FACTOR',
        school_id=school_id,
        school_year=rpms_folder_school_year
    )
    
    plus_factor.class_work_id = str(uuid4())
    
    plus_factor.objectives = forms_text.form_for_plus_factor_highly_proficient()
    
    plus_factor.save()


def update_rpms_attachment( rpms_attachment : models.RPMSAttachment, content : dict):

    rpms_attachment.check_date = timezone.now()
    rpms_attachment.grade = content
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



def generate_report(school : models.School):
    if not school:
            return None
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
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
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
    styles.add(ParagraphStyle(name='SchoolName', alignment=1, fontSize=18, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='SchoolYear', alignment=1, fontSize=16))

    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph(school.school_name, styles['SchoolName']))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph(f"{school_year_text}", styles['SchoolYear']))

    elements.append(Spacer(1, 0.5*inch))

    # Add table headers
    table_data = [
        ["Name of Teachers", "KRA 1", "KRA 2", "KRA 3", "KRA 4", "PLUS FACTOR", "Total Score", "Final Rating" ,"Adjective Rating", ],
        # ["Jessica Sanchez Ramirez", "90", "85", "88", "92", "80", "80", "0.34","Very Good"],
        # ["John Doe", "80", "78", "85", "88", "75","80", "0.34","Very Good"],
        # ["Jane Smith", "85", "88", "90", "89", "82","80", "0.34", "Very Good"]
    ]
    
    teachers = models.People.objects.filter(school_id=school.school_id).filter(is_deactivated = False, is_accepted = True)
    for teacher in teachers:
        teacher_data_individual = []
        teacher_data_individual.append(teacher.fullname)
        
        result = get_rpms_forms_by_title(teacher.employee_id)
        total_score = 0.0
        for kra, scores in result.items():
            total_score += sum(scores) / len(scores) if len(scores) > 0 else 0
            teacher_data_individual.append(sum(scores) / len(scores) if len(scores) > 0 else 0)
        teacher_data_individual.append(total_score)
        ipcrf = models.IPCRFForm.objects.filter(employee_id=teacher.employee_id, form_type='PART 1').order_by('-created_at').first()
        rating = ipcrf.evaluator_rating if ipcrf else 0.0
        teacher_data_individual.append(rating)
        adjective_rating = classify_ipcrf_score(rating)
        teacher_data_individual.append(adjective_rating)
        
        table_data.append(teacher_data_individual)

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

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer and write it to the response.
    buffer.seek(0)
    return buffer
    # return HttpResponse(buffer, as_attachment=True, content_type='application/pdf')



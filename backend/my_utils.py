from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.templatetags.static import static


from django.utils import timezone
from datetime import datetime

from uuid import uuid4
from . import models

import forms_text


position = {
    'Proficient' : ('Teacher I', 'Teacher II', 'Teacher III'  ),
    'Highly Proficient' : ('Master Teacher I', 'Master Teacher II', 'Master Teacher III', 'Master Teacher IV'),
}

# from transformers import AutoModelForCausalLM, AutoTokenizer

# # Load the model and tokenizer
# model_name = "EleutherAI/gpt-neox-20b"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name)

# def generate_text(input_text):
#     inputs = tokenizer(input_text, return_tensors="pt")
#     outputs = model.generate(inputs['input_ids'], max_length=200)
#     generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
#     return generated_text



def send_verification_email(user_email, verification_code , template , masbate_locker_email , subject):
    subject = subject
    from_email = masbate_locker_email
    to_email = user_email

    # Render the HTML template
    html_content = render_to_string(template, {
        'verification_code': verification_code,
        'deped_logo' : static('logo.png')
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


def parse_date_string(date_string):
    try:
        naive_datetime = datetime.strptime(date_string, "%B %d, %Y")
        parsed_date = timezone.make_aware(naive_datetime, timezone.get_current_timezone())
        return parsed_date
    except ValueError:
        print(f"Error: The date format of '{date_string}' is incorrect.")
        return None


def get_kra_breakdown_of_a_teacher(employee_id : str):
    """
        Return dictionary of the RPMSAttachment of the teacher
        breakdown = {
            'kra' : ['KRA1 1', 'KRA 2', 'KRA 3', 'KRA 4', 'PLUS FACTOR' ],
            'averages' : [ 'avg1', 'avg2', 'avg3', 'avg4', 'avg5' ]
        }
    """

    teacher = models.People.objects.filter(employee_id=employee_id).first()
    rpms_attachments = models.RPMSAttachment.objects.filter(teacher_id=teacher.id)
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
    teachers = models.People.objects.filter(school_id=school.id)
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
    recent_ipcrf_score = teacher.get_recent_ipcrf_score()  # Assume this method returns the most recent IPCRF score
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
    school : models.School , evaluator : models.People , teacher : models.People, 
    subject : str , cot_date : str, quarter : str, cot_type : str):
    cot_form = models.COTForm.objects.create(
        school_id = school.school_id,
        employee_id = evaluator.employee_id,
        evaluated_id = teacher.employee_id
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
        content["Questions"] = {
            "1" : {
                "Objective" : "Modeled effective applications of content knowledge within and across curriculum teaching areas. *",
                "Selected" : "0" 
            },
            "2" : {
                "Objective" : "Developed and applied effective teaching strategies to promote critical and creative thinking, as well as other higher-order thinking skills. *",
                "Selected" : "0"
            },
            "3" : {
                "Objective" : "Modeled and supported colleagues in the proficient use of Mother Tongues, Filipino and English to improve teaching and learning, as well as to developed the learners' pride of their language, heritage and culture. *",
                "Selected" : "0"
            },
            "4" : {
                "Objective" : "Exhibited effective strategies that ensure safe and secure learning environments to enhance learning through the consistent implementation of policies, guidelines and procedures. *",
                "Selected" : "0"
            },
            "5" : {
                "Objective" : "Exhibited effective practices to foster learning environments that promote fairness, respect and care to encourage learning. *",
                "Selected" : "0"
            },
            "6" : {
                "Objective" : "Exhibited a learner-centered culture that promotes success by using effective teaching strategies that respond to their linguistic, cultural, socio-economic and religious backgrounds *",
                "Selected" : "0"
            },
            "7" : {
                "Objective" : "Developed and applied teaching strategies to address effectively the needs of learners from indigenous groups. *",
                "Selected" : "0"
            },
            "8" : {
                "Objective" : "Used effective strategies for providing timely, accurate and constructive feedback to encourage learners to reflect on and improve their own learning.  *",
                "Selected" : "0"
            }
        },
    elif cot_type == 'Proficient':
        content["Questions"] = {
            "1" : {
                "Objective" : "Applied knowledge of content within and across curriculum teaching areas. *",
                "Selected" : "0" 
            },
            "2" : {
                "Objective" : "Used a range of teaching strategies that enhance learner achievement in literacy and numeracy skills. *",
                "Selected" : "0" 
            },
            "3" : {
                "Objective" : "Applied a range of teaching strategies to develop critical and creative thinking, as well as other higher-order thinking skills. *",
                "Selected" : "0" 
            },
            "4" : {
                "Objective" : "Displayed proficient use of Mother Tongue, Filipino and English to facilitate  teaching and learning. *",
                "Selected" : "0" 
            },
            "5" : {
                "Objective" : "Established safe and secure learning environment to enhance learning through the consistent implementation of policies, guidelines, and procedures. *",
                "Selected" : "0" 
            },
            "6" : {
                "Objective" : "Maintained learning environment that promotes fairness, respect and care to encourage learning. *",
                "Selected" : "0" 
            },
            "7" : {
                "Objective" : "Established a learner-centered culture by using teaching strategies that respond  to their linguistic, cultural, socio-economic and religious backgrounds. *",
                "Selected" : "0" 
            },
            "8" : {
                "Objective" : "Adapted and used culturally appropriate teaching strategies to address the needs of learners from indigenous groups. *",
                "Selected" : "0" 
            },
            "9" : {
                "Objective" : "Used strategies for providing timely, accurate and constructive feedback to  improve learner performance. *",
                "Selected" : "0" 
            },
        }   
    
    cot_form.content = content
    cot_form.is_for_teacher_proficient = True if cot_type == 'Proficient' else False
    cot_form.save()
    return cot_form


def update_cot_form(cot_form : models.COTForm, comment : str , questions : dict[str, dict] ):
    cot_form.content['Comments'] = comment
    for q_id, q_info in questions.items():
        cot_form.content['Questions'][q_id]['Selected'] = q_info['Selected']
        
    cot_form.is_checked = True
    cot_form.save()



# "4" : {
#             "Question" : "gfdgdgfdgfd",
#             "QUALITY" : {
#                 "1" : "fdsfsdf",
#                 "2" : "fdsfsdf",
#                 "3" : "fdsfsdf",
#                 "4" : "fdsfsdf",
#                 "5" : "fdsfsdf",
#                 "Rate" : "0"
#             },
#             "EFFICIENCY" : {
#                 "1" : "fdsfsdf",
#                 "2" : "fdsfsdf",
#                 "3" : "fdsfsdf",
#                 "4" : "fdsfsdf",
#                 "5" : "fdsfsdf",
#                 "Rate" : "0"
#             },
#             "TIMELINES" : {
#                 "1" : "fdsfsdf",
#                 "2" : "fdsfsdf",
#                 "3" : "fdsfsdf",
#                 "4" : "fdsfsdf",
#                 "5" : "fdsfsdf",
#                 "Rate" : "0"
#             }
#         }


# "1" : {
#                 "Title" : "SELF-MANAGEMENT",
#                 "1" : "dssddsfds",
#                 "2" : "dssddsfds",
#                 "3" : "dssddsfds",
#                 "4" : "dssddsfds",
#                 "5" : "dssddsfds",
#                 "Selected" : []
#         },

def create_ipcrf_form_proficient( school : models.School , teacher : models.People):
    # Currently walang evaluator
    
    connection_to_other = str(uuid4())
    
    # Create part 1
    ipcrf_form_part_1 = models.IPCRFForm.objects.create(
        school_id = school.school_id,
        employee_id = teacher.employee_id,
        form_type = 'PART 1',
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
    )
    
    ipcrf_form_part_2.content_for_teacher = forms_text.form_for_ipcrf_part_2_proficient()
    ipcrf_form_part_2.connection_to_other = connection_to_other
    ipcrf_form_part_2.save()
    
    # Create part 3
    ipcrf_form_part_3 = models.IPCRFForm.objects.create(
        school_id = school.school_id,
        employee_id = teacher.employee_id,
        form_type = 'PART 3',
    )
    
    
    ipcrf_form_part_3.content_for_teacher = forms_text.form_for_ipcrf_part_3_proficient()
    ipcrf_form_part_3.connection_to_other = connection_to_other
    ipcrf_form_part_3.save()
    
    return (ipcrf_form_part_1, ipcrf_form_part_2, ipcrf_form_part_3)
    


def create_ipcrf_form_highly_proficient(school : models.School , teacher : models.People ):
    pass


def update_ipcrf_form_part_1_by_evaluator(
    school : models.School, teacher : models.People , ipcrf_form : models.IPCRFForm,
    content : dict[str, dict]
    ):
    
    ipcrf_form.content_for_teacher = content
    ipcrf_form.is_checked_by_evaluator = True
    ipcrf_form.save()


def update_iprcf_form_part_1_by_teacher(
    ipcrf_form : models.IPCRFForm,
    content : dict[str, dict]
    ):
    
    part_3 = models.IPCRFForm.objects.filter(connection_to_other=ipcrf_form.connection_to_other, form_type='PART 3').first()
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
    
    part_3.content_for_teacher['A']['Strenghts'] = Str
    part_3.content_for_teacher['A']['Development Needs'] = Dev
    
    part_3.save()
    
    ipcrf_form.content_for_teacher = content
    ipcrf_form.save()


def update_ipcrf_form_part_2_by_teacher(
    ipcrf_form : models.IPCRFForm,
    content : dict[str, dict]
    ):
    
    part_3 = models.IPCRFForm.objects.filter(connection_to_other=ipcrf_form.connection_to_other, form_type='PART 3').first()
    
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
    
    
    part_1 = models.IPCRFForm.objects.filter(connection_to_other=ipcrf_form.connection_to_other, form_type='PART 1').first()
    part_1.is_checked = True
    part_1.save()
    
    part_2 = models.IPCRFForm.objects.filter(connection_to_other=ipcrf_form.connection_to_other, form_type='PART 2').first()
    part_2.is_checked = True
    part_2.save()

# kra_1.objectives = {
#         "Instructions" : {
#             "Title" : "fsdfsdf",
#             "Owner" : "School Admin",
#             "Date" : "dsfsdf",
#             "Time" : "6:01 PM",
#             "Points" : "28 points" ,
#             "Objectives" : {
#                 "1" : {
#                     "Main Title" : "sfsdfdsf",
#                     "Title" : "dfsddf",
#                     "Bullet" : "dfsddsf"
#                 },
#                 "2" : {
#                     "Main Title" : "dsfsdfs",
#                     "Title" : "sdfsdfa",
#                     "Bullet" : "sdfsdfsd"
#                 }
#             }
#         },
#         "Objectives" : {
#             "1" : {
#                 "Content" : "sdfsafds",
#                 "Score" : "5"
#             }
#         },
#         "Comment" : " "
#     }



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
    

# TODO : UPDATE THE CONTENT OF THE RPMS CLASS WORKS HERE     
def create_rpms_class_works_for_highly_proficient(rpms_folder_id : str):
    # Create KRA 1
    kra_1 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 1: Content Knowledge and Pedagogy',
    )
    kra_1.class_work_id = str(uuid4())
    
    kra_1.objectives = {
        "Instructions" : {
            "Title" : "KRA 1: Content Knowledge and Pedagogy", 
            "Date" : "", # Added when published
            "Time" : "", # Added when published
            "Points" : "28 points" ,
            "Objectives" : {
                "1" : {
                    "Main Title" : "7% | Objective 1 (Applied knowledge of content within and across curriculum teaching areas)",
                    "Title" : "Means of Verification (MOV)",
                    "Bullet" : "Classroom Observation Tool (COT) rating sheet/s or inter-observer agreement form/s "
                },
                "2" : {
                    "Main Title" : "7% | Objective 2 (Used a range of teaching strategies that enhance learner achievement in literacy and numeracy skills.)",
                    "Title" : "Means of Verification (MOV)",
                    "Bullet" : "Classroom Observation Tool (COT) rating sheet/s or inter-observer agreement form/s "
                },
                "3" : {
                    "Main Title" : "7% | Objective 3 (Applied a range of teaching strategies to develop critical and creative thinking, as well as other higher-order thinking skills.)",
                    "Title" : "Means of Verification (MOV)",
                    "Bullet" : "Classroom Observation Tool (COT) rating sheet/s or inter-observer agreement form/s "
                },
                "4" : {
                    "Main Title" : "7% | Objective 4 (Displayed proficient use of Mother Tongue, Filipino, and English to facilitate teaching and learning.)",
                    "Title" : "Means of Verification (MOV)",
                    "Bullet" : "Classroom Observation Tool (COT) rating sheet/s or inter-observer agreement form/s"
                }
            }
        },
        "Comment" : " "
    }
    
    kra_1.save()
    
    # Create KRA 2
    kra_2 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 2: Curriculum Knowledge and Pedagogy',
    )
    kra_2.class_work_id = str(uuid4())
    
    kra_2.objectives = {
        "Instructions" : {
            "Title" : "KRA 2: Curriculum Knowledge and Pedagogy",
            "Date" : "", # Added when published
            "Time" : "", # Added when published
            "Points" : "28 points" ,
            "Objectives" : {
                "1" : {
                    "Main Title" : "7% | Objective 5 (Applied knowledge of content within and across curriculum teaching areas)",
                    "Title" : "Means of Verification (MOV)",
                    "Bullet" : "Classroom Observation Tool (COT) rating sheet/s or inter-observer agreement form/s "
                },
            }
        }
    }

    kra_2.save()















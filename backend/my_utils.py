from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.templatetags.static import static


from django.utils import timezone
from datetime import datetime

from uuid import uuid4
from . import models

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
    
    domains = {}
    
    domains['Content Knowledge and Pedagogy'] = {
        "1" : {
            "Question" : "Applied knowledge of content within and across curriculum teaching areas (PPST 1.1.2)",
            "QUALITY" : {
                "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "2" : "Demonstrated Level 4 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms",
                "3" : "Demonstrated Level 5 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms",
                "4" : "Demonstrated Level 6 in Objective 1 as  shown in COT rating sheets / inter-observer agreement forms",
                "5" : "Demonstrated Level 7 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms",
                "Rate" : "0"
            },
            "EFFICIENCY" : {
                "1" : "No acceptable evidence was shown", 
                "3" : "Objective was met but instruction exceeded the allotted time", 
                "5" : "Objective was met within the allotted time",
                "Rate" : "1"
            }
        },
        "2" : {
            "Question" : "Used a range of teaching strategies that enhance learner achievement in literacy and numeracy skills (PPST 1.4.2)",
            "QUALITY" : {
                "1" : "Demonstrated Level 3 in the objective as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "2" : "Demonstrated Level 4 in the objective as shown in COT rating sheets / inter-observer agreement forms",
                "3" : "Demonstrated Level 5 in the objective as shown in COT rating sheets / inter-observer agreement forms",
                "4" : "Demonstrated Level 6 in the objective as shown in COT rating sheets / inter-observer agreement forms",
                "5" : "Demonstrated Level 7 in the objective as shown in COT rating sheets / inter-observer agreement forms",
                "Rate" : "0"
            },
            "EFFICIENCY" : {
                "1" : "No acceptable evidence was shown", 
                "3" : "Objective was met but instruction exceeded the allotted time", 
                "5" : "Objective was met within the allotted time",
                "Rate" : "0"
            }, 
        },
        "3" : {
            "Question" : "Applied a range of teaching strategies to develop critical and creative thinking, as well as other higher-order thinking skills (PPST 1.5.2)",
            "QUALITY" : {
                "1" : "Demonstrated Level 3 in the objective as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "2" : "Demonstrated Level 4 in the objective as shown in COT rating sheets / inter-observer agreement forms",
                "3" : "Demonstrated Level 5 in the objective as shown in COT rating sheets / inter-observer agreement forms",
                "4" : "Demonstrated Level 6 in the objective as shown in COT rating sheets / inter-observer agreement forms",
                "5" : "Demonstrated Level 7 in the objective as shown in COT rating sheets / inter-observer agreement forms",
                "Rate" : "0"
            },
            "EFFICIENCY" : {
                "1" : "No acceptable evidence was shown", 
                "3" : "Objective was met but instruction exceeded the allotted time", 
                "5" : "Objective was met within the allotted time",
                "Rate" : "0"
            }
        },
        "4" : {
            "Question" : "Displayed proficient use of Mother Tongue, Filipino and English to facilitate teaching and learning (PPST 1.6.2)",
            "QUALITY" : {
                "1" : "Demonstrated Level 3 in the objective as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "2" : "Demonstrated Level 4 in the objective as shown in COT rating sheets / inter-observer agreement forms",
                "3" : "Demonstrated Level 5 in the objective as shown in COT rating sheets / inter-observer agreement forms",
                "4" : "Demonstrated Level 6 in the objective as shown in COT rating sheets / inter-observer agreement forms",
                "5" : "Demonstrated Level 7 in the objective as shown in COT rating sheets / inter-observer agreement forms",
                "Rate" : "0"
            },
            "EFFICIENCY" : {
                "1" : "No acceptable evidence was shown", 
                "3" : "Objective was met but instruction exceeded the allotted time", 
                "5" : "Objective was met within the allotted time",
                "Rate" : "0"
            }
        }
        
    }

    domains['Learning Environment & Diversity of Learners'] = {
        "5" : {
            "Question" : "Established safe and secure learning environments to enhance learning through the consistent implementation of policies",
            "QUALITY" : {
                "1" : "Demonstrated Level 3 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "2" : "Demonstrated Level 4 as shown in COT rating sheets / inter-observer agreement forms",
                "3" : "Demonstrated Level 5 as shown in COT rating sheets / inter-observer agreement forms",
                "4" : "Demonstrated Level 6 as shown in COT rating sheets / inter-observer agreement forms",
                "5" : "Demonstrated Level 7 as shown in COT rating sheets / inter-observer agreement forms",
                "Rate" : "0"
            },
            "EFFICIENCY" : {
                "1" : "No acceptable evidence was shown", 
                "3" : "Objective was met but instruction exceeded the allotted time", 
                "5" : "Objective was met within the allotted time",
                "Rate" : "0"
            }, 
        },
        "6" : {
            "Question" : "Maintained learning environment that promote fairness, respect and care to encourage learning (PPST 2.2.2)",
            "QUALITY" : {
                "1" : "Demonstrated Level 3 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "2" : "Demonstrated Level 4 as shown in COT rating sheets / inter-observer agreement forms",
                "3" : "Demonstrated Level 5 as shown in COT rating sheets / inter-observer agreement forms",
                "4" : "Demonstrated Level 6 in the objective as shown in COT rating sheets / inter-observer agreement forms",
                "5" : "Demonstrated Level 7as shown in COT rating sheets / inter-observer agreement forms",
                "Rate" : "0"
            },
            "EFFICIENCY" : {
                "1" : "No acceptable evidence was shown", 
                "3" : "Objective was met but instruction exceeded the allotted time", 
                "5" : "Objective was met within the allotted time",
                "Rate" : "0"
            }, 
        },
        "7" : {
            "Question" : "Established a learner - centered culture by using teaching strategies that respond to their linguistic, cultural, socioeconomic and religious",
            "QUALITY" : {
                "1" : "Demonstrated Level 3 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "2" : "Demonstrated Level 4 as shown in COT rating sheets / inter-observer agreement forms",
                "3" : "Demonstrated Level 5 as shown in COT rating sheets / inter-observer agreement forms",
                "4" : "Demonstrated Level 6 as shown in COT rating sheets / inter-observer agreement forms",
                "5" : "Demonstrated Level 7 as shown in COT rating sheets / inter-observer agreement forms",
                "Rate" : "0"
            },
            "EFFICIENCY" : {
                "1" : "No acceptable evidence was shown", 
                "3" : "Objective was met but instruction exceeded the allotted time", 
                "5" : "Objective was met within the allotted time",
                "Rate" : "0"
            }, 
        },
        "8" : {
            "Question" : "Adapted and used culturally appropriate teaching strategies to address the needs of learners from indigenous groups (PPST 3.5.2) ",
            "QUALITY" : {
                "1" : "Demonstrated Level 3 in the objective as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown or in the lesson plan and annotation provided",
                "2" : "Demonstrated Level 4 in the objective as shown in COT rating sheets / inter-observer agreement forms or in the lesson plan and annotation provided",
                "3" : "Demonstrated Level 5 in the objective as shown in COT rating sheets / inter-observer agreement forms or in the lesson plan and annotation provided",
                "4" : "Demonstrated Level 6 in the objective as shown in COT rating sheets / inter-observer agreement forms or in the lesson plan and annotation provided",
                "5" : "Demonstrated Level 7 as shown in COT rating sheets / inter-observer agreement forms or in the lesson plan and annotation provided",
                "Rate" : "0"
            },
            "EFFICIENCY" : {
                "1" : "No acceptable evidence was shown", 
                "3" : "Objective was met but instruction exceeded the allotted time", 
                "5" : "Objective was met within the allotted time",
                "Rate" : "0"
            },
        }
    }
    
    domains['Curriculum and Planning & Assessment and Reporting'] = {
        "9" : {
            "Question" : "Set achievable and appropriate learning outcomes that are aligned with learning competencies  (PPST 4.4.2)",
            "QUALITY" : {
                "1" : "No acceptable evidence was shown",
                "2" : "Set learning outcomes were not achievable or  appropriate, and were aligned with the learning competencies, as shown in the MOV submitted",
                "3" : "Set learning outcomes were achievable and appropriate, and were aligned with the learning competencies, as shown in the MOV submitted",
                "4" : "Set learning outcomes were achievable and appropriate, and contributed to the understanding of the next related competency, as shown in the MOV submitted",
                "5" : "Set learning outcomes were achievable and appropriate, and led to the attainment of the next related competency, as shown in the MOV submitted",
                "Rate" : "0"
            },
            "EFFICIENCY" : {
                "1" : "No acceptable evidence was shown",
                "2" : "Less than half of the learning outcomes set were aligned with the learning competencies as shown in the MOV submitted",
                "3" : "At least half of the learning outcomes set were aligned with the learning competencies as shown in the MOV submitted",
                "4" : "Majority of the learning outcomes set were aligned with the learning competencies as shown in the MOV submitted",
                "5" : "All of the learning outcomes set were aligned with the learning competencies as shown in the MOV submitted",
                "Rate" : "0"
            }
        },
        "10" : {
            "Question" : "Used strategies for  providing timely, accurate and constructive feedback to improve learner performance  (PPST 5.3.2)",
            "QUALITY" : {
                "1" : "Demonstrate Level 6 in the objective as shown in COT rating sheet / inter-observer agreement forms or No acceptable evidence was shown",
                "2" : "Demonstrate Level 4 in the objective as shown in COT rating sheet / inter-observer agreement forms",
                "3" : "Demonstrate Level 5 in the objective as shown in COT rating sheet / inter-observer agreement forms",
                "4" : "Demonstrate Level 6 in the objective as shown in COT rating sheet / inter-observer agreement forms",
                "5" : "Demonstrate Level 7 in the objective as shown in COT rating sheet / inter-observer agreement forms",
                "Rate" : "0"
            },
            "EFFICIENCY" : {
                "1" : "No acceptable evidence was shown", 
                "3" : "Objective was met but instruction exceeded the allotted time", 
                "5" : "Objective was met within the allotted time",
                "Rate" : "0"
            } 
        },
        "11" : {
            "Question" : "Utilized  assessment data to inform the modification of teaching and learning practices and programs (PPST 5.5.2)",
            "QUALITY" : {
                "1" : "No acceptable evidence was shown",
                "2" : "Analyzed learners' mastered skills based on the frequency of errors and correct responses as evidenced by a list of identified least / most mastered skills",
                "3" : "Planned for teaching and learning strategy and/or program based on learners' assessment data as evidenced by a list of identified least / most mastered skills with supporting MOV No. 3",
                "4" : "Develop material based on learners' assessment data as evidenced by a list of identified least / most mastered skills with supporting MOV  No. 2",
                "5" : "Implemented a teaching and learning strategy / program using materials based on learners' assessment data as evidenced by a list of identified least / most mastered skills with supporting MOV No. 1",
                "Rate" : "0"
            }, 
            "TIMELINES" : {
                "1" : "No acceptable evidence was shown",
                "2" : "Submitted MOV/s showed utilization of assessment data across 1 quarters",
                "3" : "Submitted MOV/s showed utilization of assessment data across 2 quarters",
                "4" : "Submitted MOV/s showed utilization of assessment data across 3 quarters",
                "5" : "Submitted MOV/s showed utilization of assessment data across 4 quarters",
                "Rate" : "0"
            }
        }
    }
    
    domains['Community Linkages and Professional Engagement & Personal Growth and Professional Development'] = {
        "12" : {
            "Question" : "Built relationships with parents/guardians and the wider school community to facilitate involvement in the educative process (PSST 6.2.2.)",
            "QUALITY" : {
                "1" : "No acceptable evidence was shown",
                "2" : "Communicated with and obtained response from parents/guardians and/or wider school community to facilitate involvement  in the educative process as evidenced by MOV no. 1 or 2",
                "3" : "Secured collaboration with parents/guardians and/or wider school community to facilitate involvement  in the educative process as evidenced by one MOV no. 1 or 2",
                "4" : "Sustained engagement with parents/guardians and/or wider school community to facilitate involvement  in the educative process as evidenced by 2 or more of MOV no. 1 or 2",
                "5" : "Sustained engagement through regular communication of learners' needs, progress and achievement to key stakeholders, including parents/guardians, as shown in the MOV submitted ",
                "Rate" : "0"
            }, 
            "TIMELINES" : {
                "1" : "No acceptable evidence was shown",
                "2" : "Showed engagement with parents/guardians and the wider school community across 1 quarters",
                "3" : "Showed engagement with parents/guardians and the wider school community across 2 quarters",
                "4" : "Showed engagement with parents/guardians and the wider school community across 3 quarters",
                "5" : "Showed engagement with parents/guardians and the wider school community across 4 quarters",
                "Rate" : "0"
            }
        },
        "13" : {
            "Question" : "Participated in professional networks to share knowledge and to enhance practice (PPST 7.3.2)",
            "QUALITY" : {
                "1" : "No acceptable evidence was shown",
                "2" : "Participated in any professional network/activity that does not requires output to share knowledge and to to enhance practice as evidenced by the submitted MOV",
                "3" : "Participated in any professional network/activity that requires output* and proof of implementation** to enhance practice as evidenced by the submitted MOV",
                "4" : "Participated in any professional network/activity that requires output* and proof of implementation** within the department/grade level to share knowledge and to enhance practice as evidenced by the submitted MOV",
                "5" : "Participated in any professional network/activity that requires output* and proof of implementation** within the school to share knowledge and to enhance practice as evidenced by the submitted MOV",
                "Rate" : "0"
            }, 
            "TIMELINES" : {
                "1" : "No acceptable evidence was shown",
                "2" : "Participated in professional networks to share knowledge and to enhance practice across 1 quarters",
                "3" : "Participated in professional networks to share knowledge and to enhance practice across 2 quarters",
                "4" : "Participated in professional networks to share knowledge and to enhance practice across 3 quarters",
                "5" : "Participated in professional networks to share knowledge and to enhance practice across 4 quarters",
                "Rate" : "0"
            }
        },
        "14" : {
            "Question" : "Developed a personal improvement plan based on reflection of one's practice and ongoing professional learning (PPST 7.4.2)",
            "QUALITY" : {
                "1" : "No acceptable evidence was shown",
                "2" : "Accomplished the e-SAT at the beginning of the school year as evidence by MOV 1",
                "3" : "Set professional development goals based on e-SAT results as evidence by MOV 2",
                "4" : "Discussed progress on professional development goals with the rater during the mid-year review  as evidenced by MOV 3",
                "5" : "Updated professional goals during Phase II of the RPMS Cycle as evidenced by MOV 4",
                "Rate" : "0"
            },
            "EFFICIENCY" : {
                "1" : "No acceptable evidence was shown",
                "2" : "Submitted 1 acceptable MOV's",
                "3" : "Submitted 2 acceptable MOV's",
                "4" : "Submitted 3 acceptable MOV's",
                "5" : "Submitted 4 acceptable MOV's",
                "Rate" : "0"
            },
            "TIMELINES" : {
                "1" : "No acceptable evidence was shown",
                "2" : "Only one (1) of the submitted MOVs was accomplished within the prescribed RPMS Phase",
                "3" : "Two (2) of the submitted MOVs were accomplished within the prescribed RPMS Phase",
                "4" : "Three (3) of the submitted MOVs were accomplished within the prescribed RPMS Phase",
                "5" : "All four (4) submitted MOVs were accomplished within the prescribed RPMS Phase",
                "Rate" : "0"
            }
        }
    }
    
    domains['PLUS FACTOR'] = {
        "15" : {
            "Question" : "Performed various related works/activities that contribute to the teaching learning process",
            "QUALITY" : {
                "1" : "No acceptable evidence was shown",
                "2" : "Performed at least (1) related work/activity that contributed to the teaching-learning process within the class as evidenced by the submitted MOV.",
                "3" : "Performed at least (1) related work/activity that contributed to the teaching-learning process within the learning area/department as evidenced by the submitted MOV.",
                "4" : "Performed at least (1) related work/activity that contributed to the teaching-learning process within the school/Community Learning Center (CLC) as evidenced by the submitted MOV.",
                "5" : "Performed at least (1) related work/activity that contributed to the teaching-learning process beyond the school/Community Learning Center (CLC) as evidenced by the submitted MOV.",
                "Rate" : "0"
            },
            "EFFICIENCY" : {
                "1" : "No acceptable evidence was shown",
                "2" : "Submitted MOV that shows considerable overlap with, hence significantly affecting the performance of the actual teaching-learning process.",
                "3" : "Submitted MOV that shows reasonable interlap with the actual teaching-learning process, as evidenced by the annotation provided.",
                "4" : "Submitted MOVs that details the perceived positive contribution to the teaching-learning process, as evidenced by the annotation provided.",
                "5" : "Submitted MOVs that details the achieved positive contribution to the teaching-learning process, as evidenced by the annotation provided.",
                "Rate" : "0"
            },
            "TIMELINES" : {
                "1" : "No acceptable evidence was shown",
                "2" : "Submitted MOVs were distributed across 1 quarters",
                "3" : "Submitted MOVs were distributed across 2 quarters",
                "4" : "Submitted MOVs were distributed across 3 quarters",
                "5" : "Submitted MOVs were distributed across 4 quarters",
                "Rate" : "0"
            }
        },
    }
    
    ipcrf_form_part_1.content_for_teacher = domains
    ipcrf_form_part_1.content_for_evaluator = domains
    ipcrf_form_part_1.connection_to_other = connection_to_other
    ipcrf_form_part_1.save()

    # Create part 2
    ipcrf_form_part_2 = models.IPCRFForm.objects.create(
        school_id = school.school_id,
        employee_id = teacher.employee_id,
        form_type = 'PART 2',
    )
    
    ipcrf_form_part_2.content_for_teacher = {
        "1" : {
                "Title" : "SELF-MANAGEMENT",
                "1" : "Sets personal goals and direction, needs and development.",
                "2" : "Undertakes personal actions and behavior that are clear and purposive and takes into account personal goals and values congruent to that of the organization. ",
                "3" : "Displays emotional maturity and enthusiasm for and is challenged by higher goals.",
                "4" : "Prioritizes work tasks and schedules (through Gantt chants, checklists, etc.) to achieve goals.",
                "5" : "Sets high quality, challenging, realistic goals for self and others. ",
                "Selected" : []
        },
        "2" : {
                "Title" : "Professionalism and Ethics",
                "1" : "Demonstrates the values and behavior enshrined in the Norms and Conduct and Ethical Standards for Public Officials and Employees (RA 6713).",
                "2" : "Practices ethical and professional behavior and conduct taking into account the impact of his/her actions and decisions.",
                "3" : "Maintains a professional image: being trustworthy, regularity of attendance and punctuality, good grooming and communication.",
                "4" : "Makes personal sacrifices to meet the organization's needs.",
                "5" : "Acts with a sense of urgency and responsibility to meet the organization's needs, improve system and help others improve their effectiveness.",
                "Selected" : []
        },
        "3" : {
                "Title" : "Results Focus",
                "1" : "Achieves results with optimal use of time and resources most of the time.",
                "2" : "Avoids rework, mistakes and wastage through effective work methods by placing organizational needs before personal needs.",
                "3" : "Delivers error-free outputs most of the time by conforming to standard operating procedures correctly and consistently. Able to produce very satisfactory quality work in terms of usefulness/acceptability and completeness with no supervision required.",
                "4" : "Expresses a desire to do better and may express frustration at waste or inefficiency. May focus on new or more precise ways of meeting goals set.",
                "5" : "Makes specific changes in the system or in own work methods to improve performance. Examples may include doing something better, faster, at a lowest cost, more efficiently, or improving quality, customer satisfaction, morale, without setting any specific goal.",
                "Selected" : []
        },
        "4" : {
                "Title" : "Teamwork",
                "1" : "Willingly does his/her share of responsibility.",
                "2" : "Promotes collaboration and removes barrier to teamwork and goal accomplishment across the organization. ",
                "3" : "Applies negotiation principles in arriving at win-win agreements.",
                "4" : "Drives consensus and team ownership of decisions.",
                "5" : "Works constructively and collaboratively with others and across organizations to accomplish organization goals and objectives.",
                "Selected" : []
        },
        "5" : {
                "Title" : "Service Orientation",
                "1" : "Can explain and articulate organizational directions, issues and problems.",
                "2" : "Takes personal responsibility for dealing with and/or correcting customer service issues and concerns.",
                "3" : "Initiates activities that promote advocacy for men and women empowerment.",
                "4" : "Participates in updating office vision, mission, mandates and strategies based on DepEd strategies and directions.",
                "5" : "Develops and adopts service improvement program through simplified procedures that will further enhance service delivery.",
                "Selected" : []
        },
        "6" : {
                "Title" : "Innovation",
                "1" : "Examines the root cause of problems and suggests effective solutions. Foster new ideas, processes and suggests better ways to do things (cost and for operational efficiency).",
                "2" : "Demonstrates an ability to think \"beyond the box\". Continuously focuses on improving personal productivity to create higher value and results.",
                "3" : "Promotes a creative climate and inspires co-workers to develop original ideas or solutions.",
                "4" : "Translates creative thinking into tangible changes and solutions that improve the work unit and organization..",
                "5" : "Uses ingenious methods to accomplish responsibilities. Demonstrates resourcefulness and the ability to succeed with minimal resources.",
                "Selected" : []
        },
    }
    ipcrf_form_part_2.connection_to_other = connection_to_other
    ipcrf_form_part_2.save()
    
    # Create part 3
    ipcrf_form_part_3 = models.IPCRFForm.objects.create(
        school_id = school.school_id,
        employee_id = teacher.employee_id,
        form_type = 'PART 3',
    )
    
    plans = {}
    
    plans["A"] = {
                "Strenghts" : {
                    "1" : {
                        "QUALITY" : "",
                        "EFFICIENCY" : "",
                        "TIMELINES" : ""
                    },
                    "2" : {
                        "QUALITY" : "",
                        "EFFICIENCY" : "",
                        "TIMELINES" : ""
                    },
                },
                "Development Needs" : {
                    "1" : {
                        "QUALITY" : "",
                        "EFFICIENCY" : "",
                        "TIMELINES" : ""
                    },
                    "2" : {
                        "QUALITY" : "",
                        "EFFICIENCY" : "",
                        "TIMELINES" : ""
                    },
                },
                "Learning Objectives": {
                    "1" : "",
                    "2" : "",
                },
                "Intervention": {
                    "1" : "",
                    "2" : "",
                },
                "Timeline": {
                    "1" : "",
                    "2" : "",
                },
                "Resources Needs": {
                    "1" : "",
                    "2" : "",
                },
                
            },
    
    plans["B"] = {
                "Selections" : {
                    "1" : {
                        "Title" : "SELF-MANAGEMENT",
                        "Selected" : [
                            "1" , "2", "3"
                        ]
                    },
                    "2" : {
                        "Title" : "Professionalism and Ethics",
                        "Selected" : []
                    },
                },
                "Learning Objectives": {
                    "1" : "Learning Objectives Learning Objectives Learning Objectives.",
                    "2" : "Learning Objectives Learning Objectives Learning Objectives.",
                },
                "Intervention": {
                    "1" : "Learning Objectives Learning Objectives Learning Objectives.",
                    "2" : "Learning Objectives Learning Objectives Learning Objectives.",
                },
                "Timeline": {
                    "1" : "Learning Objectives Learning Objectives Learning Objectives.",
                    "2" : "Learning Objectives Learning Objectives Learning Objectives.",
                },
                "Resources Needs": {
                    "1" : "Learning Objectives Learning Objectives Learning Objectives.",
                    "2" : "Learning Objectives Learning Objectives Learning Objectives.",
                },
            }
    
    ipcrf_form_part_3.content_for_teacher = plans
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
    part_3.save()
    
    
    ipcrf_form.content_for_teacher = content
    ipcrf_form.save()


def update_ipcrf_form_part_2_by_teacher(
    ipcrf_form : models.IPCRFForm,
    content : dict[str, dict]
    ):
    
    part_3 = models.IPCRFForm.objects.filter(connection_to_other=ipcrf_form.connection_to_other, form_type='PART 3').first()
    # TODO : UPDATE THE CONTENT OF PART 3
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



# TODO : FIX THE DATA STRUCTURE EACH OF THE OBJECTIVES
def create_rpms_class_works_for_proficient(rpms_folder_id : str):
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
                    "Sub Title" : "Classroom Observation Tool (COT) rating sheet/s or inter -observer agreement form/s done through onsite / face-to-face / in-person classroom observation",
                    "Section" : "FDFDF",
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
        "Grade" : {
            
        },
        "Comment" : " "
    }
    
    kra_1.save()
    
    # Create KRA 2
    kra_2 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 2: Learning Environment and Diversity of Learners',
    )
    kra_2.class_work_id = str(uuid4())
    
    
    kra_2.objectives = {
        "Instructions" : {
            "Title" : "KRA 2: Learning Environment and Diversity of Learners", 
            "Date" : "", # Added when published
            "Time" : "", # Added when published
            "Points" : "28 points" ,
            "Objectives" : {
                "1" : {
                    "Main Title" : "7% | Objective 5 (Established safe and secure learning environments to enhance learning through the consistent implementation of policies, guidelines and procedures.)",
                    "Title" : "Means of Verification (MOV)",
                    "Bullet" : "Classroom Observation Tool (COT) rating sheet/s or inter -observer agreement form/s "
                },
                "2" : {
                    "Main Title" : "7% | Objective 6 (Maintained learning environments that promote fairness, respect and care to encourage learning.)",
                    "Title" : "Means of Verification (MOV)",
                    "Bullet" : "Classroom Observation Tool (COT) rating sheet/s or inter -observer agreement form/s "
                },
                "3" : {
                    "Main Title" : "7% | Objective 7 (Established a learner-centered culture by using teaching strategies that respond to their linguistic, cultural, socio-economic and religious backgrounds.)",
                    "Title" : "Means of Verification (MOV)",
                    "Bullet" : "Classroom Observation Tool (COT) rating sheet/s or inter -observer agreement form/s "
                },
                "4" : {
                    "Main Title" : "7% | Objective 8 (Adapted and used culturally appropriate teaching strategies to address the needs of learners from indigenous groups. )",
                    "Title" : "Means of Verification (MOV)",
                    "Bullet" : "Classroom Observation Tool (COT) rating sheet/s or inter -observer agreement form/s"
                }
            }
        },
        "Comment" : " "
    }
    
    kra_2.save()
    
    
    # Create KRA 3
    kra_3 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 3: Curriculum and Planning',
    )
    
    kra_3.class_work_id = str(uuid4())
    kra_3.objectives = {
        "Instructions" : {
            "Title" : "KRA 3: Curriculum and Planning", 
            "Date" : "", # Added when published
            "Time" : "", # Added when published
            "Points" : "21 points" ,
            "Objectives" : {
                "1" : {
                    "Main Title" : "7% | Objective 9 (Set achievable and appropriate learning outcomes that are aligned with learning competencies.)",
                    "Title" : "Means of Verification (MOV)",
                    "Bullet" : "At least one (1) lesson plan (e.g., DLP, DLL, WHLP, WLP, WLL, Lesson Exemplars, and the likes) or one lesson from a self-learning module, developed by the ratee* and used in instruction, with achievable and appropriate learning outcomes that are aligned with the learning competencies as shown in any one (1) of the following:",
                    "Sub Bullet 1" : "lecture/discussion",
                    "Sub Bullet 2" : "activity/activity sheet",
                    "Sub Bullet 3" : "performance task",
                    "Sub Bullet 4" : "rubric for assessing performance using criteria that appropriately describe the target output",
                },
                "2" : {
                    "Main Title" : "7% | Objective 10 (Used strategies for providing timely, accurate and constructive feedback to improve learner performance.)",
                    "Title" : "Means of Verification (MOV)",
                    "Bullet" : "Classroom Observation Tool (COT) rating sheet/s or inter -observer agreement form/s",
                },
                "3" : {
                    "Main Title" : "7% | Objective 11 (Utilized assessment data to inform the modification of teaching and learning practices and programs..)",
                    "Title" : "Means of Verification (MOV)",
                    "Bullet" : "A list of identified least /most mastered skills based on the frequency of errors /correct responses with any one (1) of the following supporting MOVs",
                    "Sub Bullet 1" : "accomplishment report for remedial / enhancement activities (e.g., remedial sessions, Summer Reading Camp, Phil-IRI-based reading program)",
                    "Sub Bullet 2" : "intervention material used for remediation / reinforcement / enhancement",
                    "Sub Bullet 3" : "lesson plan/activity log for remediation / enhancement utilizing of assessment data to modify teaching and learning practices or programs",
                },
            }
        },
        "Comment" : " "
    }
    
    kra_3.save()
    
    
    
    # Create KRA 4
    kra_4 = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'KRA 4:  Curriculum and Planning & Assessment and Reporting',
    )
    
    kra_4.class_work_id = str(uuid4())
    
    kra_4.objectives = {
        "Instructions" : {
            "Title" : "KRA 4:  Curriculum and Planning & Assessment and Reporting",
            "Date" : "",
            "Time" : "",
            "Points" : "21 points" ,
            "Objectives" : {
                "1" : {
                    "Main Title" : "7% | Objective 12 (Build relationships with parents/ guardians and the wider school community to facilitate involvement in the educative process. )",
                    "Title" : "Means of Verification (MOV)",
                    "Bullet" : "Any one (1) of the following:",
                    "Sub Bullet 1" : {
                            "Title" : "Proof of participation in any activity highlighting the objective, such as, but not limited the following:",
                            "Bullet 1" : "Receipt form/monitoring form during distribution of learning materials, etc.",
                            "Bullet 2" : "Commitment form to stakeholders, developed advocacy materials, certificate of participation that shows parents'/stakeholders' engagement signed by the school head, etc.",
                            "Bullet 3" : "Home visitation forms",
                            "Bullet 4" : "Any equivalent ALS form/document that highlights the objective",
                            "Bullet 5" : "Others (please specify and provide annotations)",
                        },
                    "Sub Bullet 2" : "Parent-teacher log or proof of other stakeholders meeting (e.g., one-on-one parent-teacher learner conference log; attendance sheet with minutes of online or face-to-face meeting; proof of involvement in the learners'/parents' orientation, etc.)",
                    "Sub Bullet 3" : "Any form of communication to parents/stakeholders (e.g., notice of meeting; screenshot of chat/text message/communication with parent/guardian)"
                },
                "2" : {
                    "Main Title" : "7% | Objective 13 (Participated in professional networks to share knowledge and to enhance practice )",
                    "Title" : "Means of Verification (MOV)",
                    "Bullet 1" : "Certificate of completion in a course/training",
                    "Bullet 2" : "sdfsCertificate of participation in a webinar, retooling, upskilling, and other training/ seminar/ workshop with proof of implementationdfsd",
                    "Bullet 3" : "Certificate of recognition/ speakership in a webinar and other training/ seminar/ workshop",
                    "Bullet 4" : "Any proof of participation to a benchmarking activity",
                    "Bullet 5" : "Any proof of participation in school LAC sessions (online/face-to-face) certified by the LAC Coordinator",
                    "Bullet 6" : "Others (please specify and provide annotations)",
                },
                "3" : {
                    "Main Title" : "7% | Objective 14 (Developed a personal improvement plan based on reflection of one s practice and ongoing professional learning)",
                    "Title" : "Means of Verification (MOV)",
                    "Bullet 1" : "Certification from the ICT Coordinator / School Head / Focal Person in charge of e-SAT",
                    "Bullet 2" : "IPCRF-DP",
                    "Bullet 3" : "Mid-year Review Form (MRF)",
                    "Bullet 4" : "Updated IPCRF-DP from Phase II"
                }
            }
        }, 
        "Comment" : " "

    }
    
    kra_4.save()
    
    # Create PLUS FACTOR
    plus_factor = models.RPMSClassWork.objects.create(
        rpms_folder_id = rpms_folder_id,
        title = 'PLUS FACTOR',
    )
    
    plus_factor.class_work_id = str(uuid4())
    
    plus_factor.objectives ={
        "Instructions" : {
            "Title" : "PLUS FACTOR",
            "Owner" : "School Admin",
            "Date" : "",
            "Time" : "",
            "Points" : "2 points" ,
            "Objectives" : {
                "1" : {
                    "Main Title" : "2% | Objective 15 (Performed various related works / activities that contribute to the teaching- learning process.)",
                    "Title" : "Means of Verification (MOV)",
                    "Bullet" : "Any one (1) of the following:",
                    "Sub Bullet 1" : "committee involvement;",
                    "Sub Bullet 2" : "involvement as module/learning material writer/ validator;",
                    "Sub Bullet 3" : "involvement as a resource person/speaker/learning facilitator in the RO/SDO/school-initiated TV/radio-based instruction;",
                    "Sub Bullet 4" : "book or journal authorship/co-authorship/ contributorship;",
                    "Sub Bullet 5" : "advisorship/coordinatorship/chairpersonship",
                    "Sub Bullet 6" : "participation in demonstration teaching;",
                    "Sub Bullet 7" : "participation as research presenter in a forum/ conference;",
                    "Sub Bullet 8" : "mentorship of pre-service/in-service teachers",
                    "Sub Bullet 9" : "conducted research within the rating period;",
                    "Sub Bullet 10" : "Others (please specify) with annotation on how it contributed to the teaching-learning process."
                },
            }
        },
        "Comment" : " "
        
    }
    
    plus_factor.save()
    
    
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















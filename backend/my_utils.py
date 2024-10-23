from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime

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
        parsed_date = datetime.strptime(date_string, "%B %d, %Y")
        return parsed_date
    except ValueError:
        print(f"Error: The date format of '{date_string}' is incorrect.")
        return None



def classify_ipcrf_score(score):
    if 4.5 <= score <= 5.0:
        return 'Promotion'
    elif 3.5 <= score < 4.5:
        return 'Retention'
    elif 2.5 <= score < 3.5:
        return 'Retention'
    elif 1.5 <= score < 2.5:
        return 'Termination'
    else:
        return 'Termination'


def is_proficient_faculty(people : models.People):
    if people.position in position['Proficient']:
        return True
    return False

def is_highly_proficient_faculty(people : models.People):
    if people.position in position['Highly Proficient']:
        return True
    return False


def create_cot_form(school : models.School , evaluator : models.People , teacher : models.People, subject : str , cot_date : str, quarter : str):
    cot_form = models.COTForm.objects.create(
        school_id = school.school_id,
        employee_id = evaluator.employee_id,
        evaluated_id = teacher.employee_id
    )
    
    cot_form.content = {
            "Observer ID" : f"{evaluator.employee_id}",
            "Observer Name" : f"{evaluator.fullname}",
            "Teacher Name" : f"{teacher.fullname}",
            "Teacher ID" : f"{teacher.employee_id}",
            "Subject & Grade Level" : f"{subject}",
            "Date" : f"{cot_date}",
            "Quarter": f"{quarter}",
            "Questions" : {
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
            "Comments" : ""
        }

    cot_form.save()
    return cot_form



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


def create_ipcrf_form_proficient( school : models.School , teacher : models.People):
    # Currently walang evaluator
    ipcrf_form_part_1 = models.IPCRFForm.objects.create(
        school_id = school.school_id,
        employee_id = teacher.employee_id,
        form_type = 'Part 1',
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




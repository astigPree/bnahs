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



def create_ipcrf_form_proficient( school : models.School , teacher : models.People):
    # Currently walang evaluator
    ipcrf_form_part_1 = models.IPCRFForm.objects.create(
        school_id = school.school_id,
        employee_id = teacher.employee_id,
        form_type = 'Part 1',
    )
    
    ipcrf_form_part_1.content_for_teacher = {
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
                "1" : "fdsfsdf",
                "2" : "fdsfsdf",
                "3" : "fdsfsdf",
                "4" : "Demonstrated Level 6 in the objective as shown in COT rating sheets / inter-observer agreement forms",
                "5" : "Demonstrated Level 7 in the objective as shown in COT rating sheets / inter-observer agreement forms",
                "Rate" : "0"
            },
            "EFFICIENCY" : {
                "1" : "fdsfsdf",
                "2" : "fdsfsdf",
                "3" : "fdsfsdf",
                "4" : "fdsfsdf",
                "5" : "fdsfsdf",
                "Rate" : "0"
            },
            "TIMELINES" : {
                "1" : "fdsfsdf",
                "2" : "fdsfsdf",
                "3" : "fdsfsdf",
                "4" : "fdsfsdf",
                "5" : "fdsfsdf",
                "Rate" : "0"
            }
        },
        "4" : {
            "Question" : "gfdgdgfdgfd",
            "QUALITY" : {
                "1" : "fdsfsdf",
                "2" : "fdsfsdf",
                "3" : "fdsfsdf",
                "4" : "fdsfsdf",
                "5" : "fdsfsdf",
                "Rate" : "0"
            },
            "EFFICIENCY" : {
                "1" : "fdsfsdf",
                "2" : "fdsfsdf",
                "3" : "fdsfsdf",
                "4" : "fdsfsdf",
                "5" : "fdsfsdf",
                "Rate" : "0"
            },
            "TIMELINES" : {
                "1" : "fdsfsdf",
                "2" : "fdsfsdf",
                "3" : "fdsfsdf",
                "4" : "fdsfsdf",
                "5" : "fdsfsdf",
                "Rate" : "0"
            }
        }
        
    }





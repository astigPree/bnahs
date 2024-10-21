from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime

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






from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime

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


def parse_date_string(date_string):
    try:
        parsed_date = datetime.strptime(date_string, "%B %d, %Y")
        return parsed_date
    except ValueError:
        print(f"Error: The date format of '{date_string}' is incorrect.")
        return None

# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from secret import get_secret

JSON_SECRET = get_secret()


def send_email(email_from: str, email_to: any, subject: str, html_content: str):
    try:
        sg = SendGridAPIClient(JSON_SECRET['sendgrid']['api_key'])
        message = Mail(
            from_email=email_from,
            to_emails=email_to,
            subject=subject,
            html_content=html_content + '<br><p>Powered by <a href="">Your Application</a></p>')

        sg.send(message)
    except:
        return False
    return True

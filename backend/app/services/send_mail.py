"""
This file contains the function to send an email to the user.

Attributes:
    - recipient (str): The email address used for sending emails.
    - template_data (dict): contains the reset link
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException
from app.resources.required_packages import (
    FROM_EMAIL, SMTP_PASSWORD, SMTP_PORT, SMTP_SERVER, SMTP_USERNAME)

def send_mail(recipient: str, template_data: dict):
    """
    Function to send an email using SMTP.
    """
    # Create the email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Password Reset"
    msg['From'] = FROM_EMAIL
    msg['To'] = recipient

    # Create the body of the message (HTML)
    html = f"""
    <html>
    <body>
        <p>Hi {template_data['first_name']},</p>
        <p>Please click the link below to reset your password:</p>
        <a href="{template_data['link']}">Reset Password</a>
    </body>
    </html>
    """
    part = MIMEText(html, 'html')
    msg.attach(part)

    try:
        # Connect to the server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, recipient, msg.as_string())
            return 200  # HTTP status code for success

    except Exception as original_exception:
        error_message = f"  {str(original_exception)}"
        raise HTTPException(
            status_code=500, detail=error_message
        ) from original_exception

def send_recovery_mail(token, host, email: str, first_name: str, lang: str):
    """
    Create a reset link and send it to the user.
    """
    reset_link = f"{host}/reset-password/{token}"

    # recipient = email
    # template_data = {
    #     "link": reset_link,
    #     "first_name": first_name,
    #     "lang": lang,
    # }

    # Send reset link to user
    print(reset_link)
    # send_mail(recipient, template_data)
    return 200

# -*- coding: utf-8 -*-
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

def send_email(sender_email, app_password, recipient_email, subject, body_html, attachment_path=None):
    """
    Sends an email with an optional attachment via SMTP (supports Gmail, Naver, etc.).
    
    Args:
        sender_email (str): The sender's email address.
        app_password (str): The sender's App Password (NOT login password).
        recipient_email (str): The recipient's email address.
        subject (str): Email subject line.
        body_html (str): Email body content (HTML supported).
        attachment_path (str, optional): Absolute path to the file attachment (e.g., PDF).
    
    Returns:
        bool: True if sent successfully, False otherwise.
    """
    if not sender_email or not app_password or not recipient_email:
        print("❌ Email Error: Missing email credentials or recipient.")
        return False

    # Detect SMTP Server based on sender email
    if "gmail.com" in sender_email:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
    elif "naver.com" in sender_email:
        smtp_server = "smtp.naver.com"
        smtp_port = 587
    else:
        # Fallback to Gmail or generic (User might need to configure this later if using other providers)
        print(f"⚠️ Warning: Unknown email provider for {sender_email}. Trying Gmail default.")
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

    try:
        # Create MIME Message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach Body
        msg.attach(MIMEText(body_html, 'html'))

        # Attach PDF if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                attach = MIMEApplication(f.read(), _subtype="pdf")
                attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                msg.attach(attach)
            print(f"📎 Attached file: {os.path.basename(attachment_path)}")
        elif attachment_path:
            print(f"⚠️ Warning: Attachment file not found at {attachment_path}")

        # Connect and Send
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        
        print(f"✅ Email sent successfully to {recipient_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

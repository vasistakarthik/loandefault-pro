import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_mail(recipient, subject, html_content):
    """Utility function to send emails via SMTP with robust MIME formatting."""
    import os
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.utils import formataddr

    mail_server = os.getenv("MAIL_SERVER")
    mail_port = int(os.getenv("MAIL_PORT", 587))
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")
    mail_sender = os.getenv("MAIL_DEFAULT_SENDER", mail_username)
    sender_name = "LoanDefault Pro Alerts"

    if not mail_username or not mail_password:
        print("[WARNING] SMTP not configured. Outputting to console.")
        print(f"DEBUG EMAIL:\nTo: {recipient}\nSubject: {subject}\nContent: {html_content[:200]}...")
        return False

    try:
        # Create message container - the correct MIME type is multipart/alternative
        message = MIMEMultipart("alternative")
        message["From"] = formataddr((sender_name, mail_sender))
        message["To"] = recipient
        message["Subject"] = subject
        
        # Add headers to reduce spam classification
        message["X-Priority"] = "3"  # Normal priority
        message["X-Mailer"] = "Python-SMTP-Client"
        message["Auto-Submitted"] = "auto-generated"
        message["Precedence"] = "bulk"

        # Create the plain-text version (fallback for non-HTML mail clients and spam filters)
        import re
        text_content = re.sub('<[^<]+?>', '', html_content) # Simple HTML to text converter
        text_content = text_content.strip()

        # Attach parts
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")

        # The last part (HTML) is given priority
        message.attach(part1)
        message.attach(part2)

        # Connect and Handshake
        server = smtplib.SMTP(mail_server, mail_port, timeout=15)
        server.ehlo()  # Say hello to the server
        
        if os.getenv("MAIL_USE_TLS", "True") == "True":
            server.starttls()  # Upgrade to secure connection
            server.ehlo()      # Say hello again over the secure link
            
        server.login(mail_username, mail_password)
        server.send_message(message)
        server.quit()
        return True
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] SMTP Delivery Failed: {error_msg}")
        return False, error_msg

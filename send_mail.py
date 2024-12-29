from custom_logging import *
import smtplib
import os
import mimetypes
from email.message import EmailMessage
from email.utils import formataddr





# define send mail
def send_email(account_pw, sender_mail_address, recipients, text, subject, sender_name, bcc=None, attachments=None, ):
    # Validate input parameters
    if not account_pw:
        logger.error("Account password is empty")
        return False

    if not isinstance(recipients, list) or len(recipients) == 0:
        logger.error("Recipients list is invalid or empty")
        return False

    if bcc is not None and not isinstance(bcc, list):
        logger.error("BCC must be a list or None")
        return False

    if not isinstance(sender_mail_address, str) or "@" not in sender_mail_address:
        logger.error("Sender email address is not valid")
        return False

    if text is None or not isinstance(text, str) or len(text) < 10:
        logger.error("Message text is very short, empty or not valid")
        return False

    if subject is None or not isinstance(subject, str) or len(subject) < 10:
        logger.error("Subject is empty or not valid")
        return False

    # Create email message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = formataddr((sender_name, sender_mail_address))
    msg['To'] = ", ".join(recipients)

    if bcc:
        msg['Bcc'] = ", ".join(bcc)

    msg.set_content(text)

    # Attach files
    if attachments:
        for file_path in attachments:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                file_type, _ = mimetypes.guess_type(file_path)
                if file_type is None:
                    file_type = "application/octet-stream"
                main_type, sub_type = file_type.split('/', 1)

                with open(file_path, 'rb') as file:
                    msg.add_attachment(file.read(), maintype=main_type, subtype=sub_type,
                                       filename=os.path.basename(file_path))
                logger.info(f"Attached file: {file_path}")
            else:
                logger.warning(f"Attachment file not found or is not a file: {file_path}")
                return False

    # Connect to the SMTP server and send the email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_mail_address, account_pw)
            server.send_message(msg)
            logger.info(f"Email sent successfully to {', '.join(recipients)}")
            return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


# define send specific notify mail
def send_notifyclient(account_pw, sender_mail_address, recipients, bcc, sal_mail, text, lea_mail, subject, own_mail_nm, attachments=None):
    send_email(account_pw=account_pw, sender_mail_address=sender_mail_address, recipients=recipients
               , bcc=[bcc], text=f"{sal_mail}\n\n{text}\n\n{lea_mail}", subject=subject, sender_name=own_mail_nm, attachments=attachments)



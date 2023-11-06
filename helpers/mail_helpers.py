import logging
import mimetypes
import os
import smtplib, ssl
from email.header import Header
from email.message import EmailMessage
from email.utils import formataddr

from models.route_model import EmpData



SENDER_EMAIL = "sender@example.com"
SENDER_PASSWORD = "senderpassword"

def sendMail(receiver_email, subject, body, files=None, cc=None, bcc=None):
    try:
        # Create a multipart message and set headers
        sender_email = SENDER_EMAIL
        sender_password = SENDER_PASSWORD

        message = EmailMessage()
        message["From"] = formataddr((str(Header("HeaderLabel", 'utf-8')), sender_email))
        message["To"] = receiver_email
        if cc is not None:
            message["cc"] = cc
        if bcc is not None:
            message["bcc"] = bcc
        message["Subject"] = subject


        # Add body to email
        message.add_alternative(body, subtype="html")
        if files is not None:
            for fl in files:
                if os.path.isfile(fl):
                    file_name = os.path.basename(fl)
                    mime_type, _ = mimetypes.guess_type(fl)
                    with open(fl, "rb") as fp:
                        file_data = fp.read()
                        message.add_attachment(
                            file_data,
                            maintype=mime_type.split("/")[0],
                            subtype=mime_type.split("/")[1],
                            filename=file_name
                        )
                        
        text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, text)
            server.quit()
    
        return True
    except Exception as ex:
        logging.error(f"sendMail Exception: {ex}")
        return False

# eaxmple how to send email

def sendEmailOtp(fullname, email, otp):

    subject = "Email Verification OTP for Email Update"
    body = """\
            <html>
            <body>
                <p>Hello {},<br>
                    Someone is trying to update email on your profile.
                    To ensure the security of your account, we require you to verify your existing email address. <br><br>
                    <b>Your OTP is {}.</b><br><br>
                    Please note that this OTP code is valid for the next 15 minutes. If you do not complete the verification within this time frame, you will need to request a new OTP.
                    <br>
                    If you did not request this change or believe it to be unauthorized, please contact our customer support immediately at [Customer Support Email or Phone Number].
                </p>
                <p>Regards,<br>
                    [Email Sender]
                </p>
            </body>
            </html>
            """.format(fullname, otp)

    return sendMail(email, subject, body)


def sendForgetPasswordOtp(fullname, email, otp):

    subject = "Password Reset OTP"
    body = """\
            <html>
            <body>
                <p>Hello {},<br>
                   We received a request to reset the password for your account associated with {} on [Your Website or App Name]. 
                   To complete the password reset process, please use the following One-Time Password (OTP):<br/><br/>
                   <b>Your OTP is {}.</b><br><br>
                   This OTP is valid for 15 minutes. Please do not share this OTP with anyone for your security. 
                   If you did not initiate this password reset request, please disregard this email.
                </p>
                <p>Regards,<br>
                    [Email Sender]
                </p>
            </body>
            </html>
            """.format(fullname, email, otp)

    return sendMail(email, subject, body)

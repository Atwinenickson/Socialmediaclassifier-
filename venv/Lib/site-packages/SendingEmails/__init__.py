import base64
import os
import json
import sendgrid
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName,FileType, Disposition, ContentId)
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import urllib.request as urllib
from sendgrid.helpers.mail import *


class Email(object):

    def __init__(self):
        pass

    def MailGrid(self,*args,**kwargs):
        mail_txt = Content('text/plain',emailbody)
        message = Mail(
            from_email=sendermail,
            to_emails=recivermail,
            subject=subject,
            html_content=htmlcontent
            )
        message.add_content(mail_txt)
        if attach is not None:
            if os.path.isfile(attach):
                head, tail = os.path.split(attach)
                with open(attach, 'rb') as f:
                    data = f.read()
                    f.close()
                encoded = base64.b64encode(data).decode()
            else:
                encoded = attach
            attachment = Attachment()
            attachment.file_content = FileContent(encoded)
            attachment.file_type = FileType('application/pdf')
            attachment.file_name = FileName(tail)
            attachment.disposition = Disposition('attachment')
            attachment.content_id = ContentId('Example Content ID')
            message.attachment = attachment
        SENDGRID_API_KEY = "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"
        sendgrid_client = sendgrid.SendGridAPIClient(SENDGRID_API_KEY )
        response = sendgrid_client.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    def SMTPMail(self,*args,**kwargs):

        subject = subject
        body = body
        sender_email = senderemail
        receiver_email = receiveremail
        password = senderpassword

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        #message["Bcc"] = Bccmail
        if attach is not None:
            message.attach(MIMEText(body, "plain"))
            head, tail = os.path.split(attach)
            filename = attach
            with open(filename, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {tail}",
            )
            message.attach(part)
        text = message.as_string()
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)


'''
Very simple and unicode friendly way to send email message from Python code.

Usage:

    sudo pip install send_email_message
    from send_email_message import send_email_message

    email_config = dict(
        host='smtp.gmail.com',
        port=587,
        tls=True, // Or ssl=True with another port.
        user='admin@example.com',
        password='password',
        from_name='Example Site',
        # Default: encoding='utf-8'
    )

    send_email_message(
        to='denisr@denisr.com',
        subject='Example News',
        text='Please see http://example.com/',
        html='<html><body>Please see <a href="http://example.com/">example.com</a></body></html>',
        **email_config
    )

Rare usage:

    login_plain=True, # Some servers are OK with TLS, but require "LOGIN PLAIN" auth inside encrypted session.
    debug=True, # Enables debug output.

send_email_message version 0.1.5
Copyright (C) 2013-2015 by Denis Ryzhkov <denisr@denisr.com>
MIT License, see http://opensource.org/licenses/MIT
'''

#### import

from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

#### encoded

def encoded(s, encoding):
    return s.encode(encoding) if isinstance(s, unicode) else s

#### send_email

def send_email_message(to, subject='', text='', html='', encoding='utf-8', host='localhost', port=25, ssl=False, tls=False, login_plain=False, user='admin@localhost', password='', from_name='', debug=False):

    SMTP = smtplib.SMTP_SSL if ssl else smtplib.SMTP
    smtp = SMTP(host, port)

    if debug:
        smtp.set_debuglevel(True)

    if not ssl and tls:
        smtp.starttls()

    if login_plain:
        smtp.ehlo()
        smtp.esmtp_features['auth'] = 'LOGIN PLAIN'

    if password:
        smtp.login(user, password)

    user = encoded(user, encoding)
    if from_name:
        user = '{from_name} <{user}>'.format(from_name=encoded(from_name, encoding), user=user)

    msg = MIMEMultipart('alternative')
    msg['From'] = user
    msg['To'] = encoded(to, encoding)
    msg['Subject'] = Header(encoded(subject, encoding), encoding)

    for body, subtype in (
        (text, 'plain'),
        (html, 'html'),
    ):
        if body:
            msg.attach(MIMEText(encoded(body, encoding), subtype, encoding))

    smtp.sendmail(user, to, msg.as_string())

    smtp.quit()

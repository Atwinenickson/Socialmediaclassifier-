__version__ = '0.1.0'

from flask import current_app as app
from flask_mail import Message
from flask import render_template


def send_mail(subject, recipient, template, **template_kwargs):
    """Send an email via the Flask-Mail extension (based on send_mail() in flask-security utils.py)."""

    msg = Message(subject,
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[recipient])

    msg.body = render_template('%s.txt' % template, **template_kwargs)
    msg.html = render_template('%s.html' % template, **template_kwargs)

    mail = app.extensions.get('mail')
    mail.send(msg)


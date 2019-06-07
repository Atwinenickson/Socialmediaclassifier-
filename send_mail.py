from flask import current_app as app
from flask_mail import Message


def send_mail(
        sender=None, recipients=None, subject=None, body=None,
        is_log_msg=True):
    """Send mail using Flask-Mail and log the sent message."""
    if is_log_msg:
        log_msg = 'Email sent by site\n'
        log_msg += 'From: <{0}>\n'.format(sender)
        log_msg += 'To: {0}\n'.format(recipients)
        log_msg += 'Subject: {0}\n'.format(subject)
        log_msg += body

        app.logger.info(log_msg)

    if app.debug:
        return

    msg = Message(
        subject,
        sender=sender,
        recipients=recipients)
    msg.body = body

    app.mail.send(msg)
	
	
	
	
	
	
	#https://github.com/flask-admin/flask-admin/blob/master/examples/auth-flask-login/app.py
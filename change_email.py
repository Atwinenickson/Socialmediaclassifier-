from flask import current_app as app
from flask import (
    abort, after_this_request, flash, redirect, render_template,
    url_for)
from flask_login import current_user
from flask_security.forms import email_required, email_validator
from flask_security.utils import (
    config_value, do_flash, get_message, get_token_status, hash_data,
    login_user, logout_user, verify_hash)
from flask_wtf import FlaskForm
from werkzeug.local import LocalProxy
from wtforms import StringField, SubmitField
from wtforms.validators import EqualTo

from send_mail import send_mail


_security = LocalProxy(lambda: app.extensions['security'])
_datastore = LocalProxy(lambda: _security.datastore)


def _commit(response=None):
    _datastore.commit()
    return response


class ChangeEmailForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[email_required])
    new_email = StringField(
        'New email',
        validators=[email_required, email_validator])
    new_email_confirm = StringField(
        'Retype email',
        validators=[EqualTo('new_email',
                            message='Email does not match')])
    submit = SubmitField('Change email')

    def validate(self):
        if not super(ChangeEmailForm, self).validate():
            return False

        if self.email.data != current_user.email:
            self.email.errors.append('Invalid email')
            return False
        if self.email.data.strip() == self.new_email.data.strip():
            self.email.errors.append(
                'Your new email must be different than your '
                'previous email')
            return False
        return True


def confirm_change_email_token_status(token):
    """Returns the expired status, invalid status, user, and new email
    of a confirmation token. For example::
        expired, invalid, user, new_email = (
            confirm_change_email_token_status('...'))
    Based on confirm_email_token_status in Flask-Security.
    :param token: The confirmation token
    """
    expired, invalid, user, token_data = get_token_status(
        token, 'confirm', 'CONFIRM_EMAIL', return_data=True)
    new_email = None

    if not invalid and user:
        user_id, token_email_hash, new_email = token_data
        invalid = not verify_hash(token_email_hash, user.email)

    return expired, invalid, user, new_email


def generate_change_email_confirmation_link(user, new_email):
    """Based on generate_confirmation_token in Flask-Security."""
    token = generate_change_email_confirmation_token(user, new_email)
    return (
        url_for('confirm_change_email', token=token, _external=True),
        token)


def generate_change_email_confirmation_token(user, new_email):
    """Generates a unique confirmation token for the specified user.
    Based on generate_confirmation_token in Flask-Security.
    :param user: The user to work with
    :param new_email: The user's new email address
    """
    data = [str(user.id), hash_data(user.email), new_email]
    return _security.confirm_serializer.dumps(data)


def send_change_email_confirmation_instructions(user, new_email):
    """Sends the confirmation instructions email for the specified user.
    Based on send_confirmation_instructions in Flask-Security.
    :param user: The user to send the instructions to
    :param new_email: The user's new email address
    """

    confirmation_link, token = generate_change_email_confirmation_link(
        user, new_email)

    subject = 'Please confim your change of email'
    msg_body = render_template(
        'confirm_change_email.txt', user=current_user,
        new_email=new_email, confirmation_link=confirmation_link)
    send_mail(
        sender=_security.email_sender,
        recipients=[new_email],
        subject=subject, body=msg_body)


def change_user_email(user, new_email):
    """Changes the email for the specified user
    Based on confirm_user in Flask-Security.
    :param user: The user to confirm
    :param new_email: The user's new email address
    """
    if user.email == new_email:
        return False

    user.email = new_email
    _datastore.put(user)

    return True


def confirm_change_email(token):
    """View function which handles a change email confirmation request.
    Based on confirm_email in Flask-Security."""
    expired, invalid, user, new_email = (
        confirm_change_email_token_status(token))

    if not user or invalid:
        invalid = True
        do_flash(*get_message('INVALID_CONFIRMATION_TOKEN'))
    if expired:
        send_change_email_confirmation_instructions(user, new_email)
        do_flash(*(
            (
                'You did not confirm your change of email within {0}. '
                'New instructions to confirm your change of email have '
                'been sent to {1}.').format(
                    _security.confirm_email_within, new_email),
            'error'))
    if invalid or expired:
        return redirect(url_for('home'))

    if user != current_user:
        logout_user()
        login_user(user)

    if change_user_email(user, new_email):
        after_this_request(_commit)
        msg = (
            'Thank you. Your change of email has been confirmed.',
            'success')
    else:
        msg = (
            'Your change of email has already been confirmed.'
            'info')

    do_flash(*msg)
    return redirect(url_for('home'))


def change_email():
    """Change email page."""
    if not _security.confirmable:
        abort(404)

    form = ChangeEmailForm()

    if form.validate_on_submit():
        new_email = form.new_email.data
        confirmation_link, token = (
            generate_change_email_confirmation_link(
                current_user, new_email))
        flash(
            (
                'Thank you. Confirmation instructions for changing '
                'your email have been sent to {0}.').format(new_email),
            'success')

        if config_value('SEND_REGISTER_EMAIL'):
            subject = 'Confirm change of email instructions'
            msg_body = render_template(
                'confirm_change_email.txt', user=current_user,
                new_email=new_email, confirmation_link=confirmation_link)
            send_mail(
                sender=_security.email_sender,
                recipients=[new_email],
                subject=subject, body=msg_body)

        return redirect(url_for('home'))

    return render_template('change_email.html', form=form)

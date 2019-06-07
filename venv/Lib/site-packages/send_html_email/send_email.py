"""
Will populate a template with values from model instance and/or dictionary of values added to context
"""
from django.template import Context, loader, RequestContext
from django.core.mail import EmailMultiAlternatives
from utils.populate_template import populate_template, populate_template_from_instance
from django.contrib.sites.models import Site
from django.conf import settings

class HtmlEmail():
    
    """headers are a tupple of (subject, [recipients,], sender)"""
    def __init__(self, headers=False, template='default'):
        self.headers = headers
        self.html_template = u"email/%s.html" % template
        self.text_template = u"email/%s.txt" % template

    def send_email(self, html_content, text_content, forced_subject=False, forced_recipients=False, forced_sender=False):
        """ check for alternative header values, then Send email...duh!"""
        if self.headers:
            subject, recipients, sender = self.headers
        else:
            current_site = Site.objects.get_current()
            subject = ('Email from %s website' % current_site.name)
            recipients = []
            for name, email in getattr(settings, "MANAGERS"):
                recipients.append(email)
            sender = getattr(settings, "DEFAULT_FROM_EMAIL")
        
        # If values passed to send email, then overwrite previously defined values.
        if forced_subject: subject = forced_subject
        if forced_recipients: recipients = forced_recipients 
        if forced_sender: sender = forced_sender
        
        msg = EmailMultiAlternatives(subject, text_content, sender, recipients)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def send_instance_email(self, instance, additional_dict=False):
        """ Send an email populated by values from instance of object, extra data can be added with 
        optional addtional dictionary argument"""
        html_content = populate_template_from_instance(self.html_template, instance, additional_dict)
        if self.text_template:
            text_content = populate_template_from_instance(self.text_template, instance, additional_dict)
        else:
            text_content = html_content
        self.send_email(html_content, text_content)

    def send_dict_email(self,dict):
        """ Send email populated with values from dictionary"""
        html_content = populate_template(self.html_template, dict)
        if self.text_template:
            text_content = populate_template(self.text_template, dict)
        else:
            text_content = html_content
        self.send_email(html_content, text_content)


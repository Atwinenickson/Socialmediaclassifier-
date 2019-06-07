from django.template import Context, Template
from django.template.loader import get_template
from django.forms.models import model_to_dict
from django.template import Context
from django.contrib.sites.models import Site
from datetime import datetime
"""populate a template from a dictionary, a model instance or a combination of both,
returns string which an be used as email content or attachement"""

def populate_template(template, dictionary):
    temp = get_template(template)
    
    # Add mandatory values to the dictionary
    dictionary.update({'base__site': Site.objects.get_current()})
    dictionary.update({'base__now': datetime.now()})
    
    return  temp.render(Context(dictionary))

def populate_template_from_instance(template, instance, additional_dict={}):
    dictionary = model_to_dict(instance)
    if additional_dict:
        dictionary.update(additional_dict)
    
    return populate_template(template, dictionary)

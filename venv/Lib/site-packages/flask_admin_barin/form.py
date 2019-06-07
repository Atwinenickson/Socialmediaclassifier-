from flask_admin import form
from flask_admin.model.fields import InlineFormField, InlineFieldList
from wtforms import fields as f
from wtforms.fields.html5 import DateTimeField

from barin import schema as S
from barin import manager


def get_form(model):
    field_dict = {}
    for name, field in model.m.fields.items():
        form_field = get_form_field(field._schema)
        if form_field is not None:
            field_dict[name] = form_field
    return type(model.__name__ + 'Form', (form.BaseForm, ), field_dict)


def get_form_field(schema):
    if isinstance(schema, S.Unicode):
        return f.TextField()
    elif isinstance(schema, S.DateTime):
        return DateTimeField()
    elif isinstance(schema, manager.ClassManager):
        frm = get_form(schema._cls)
        return InlineFormField(frm)
    elif isinstance(schema, S.Array):
        inner = get_form_field(schema.validator)
        return InlineFieldList(inner)

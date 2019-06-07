import bson
from flask_admin.model import BaseModelView

from barin import mql
from barin import schema

from . import form
from . import filters


class ModelView(BaseModelView):

    def __init__(self, model, *args, **kwargs):
        super(ModelView, self).__init__(model, *args, **kwargs)

    @property
    def column_filters(self):
        return self.scaffold_sortable_columns()

    def get_pk_value(self, model):
        return model._id

    def scaffold_list_columns(self):
        columns = []
        for fname, field in self.model.m.fields.items():
            sch = field._schema
            if isinstance(sch, schema.Scalar):
                columns.append(fname)
        return columns

    def scaffold_sortable_columns(self):
        return self.scaffold_list_columns()

    def init_search(self):
        return False

    def scaffold_form(self):
        form_class = form.get_form(self.model)
        return form_class

    def get_list(
            self, page, sort_field, sort_desc,
            search, filters, page_size=20):
        q = self.model.m.query
        if filters:
            for flt, name, value in filters:
                q = self._filters[flt].apply(q, value)
        count = q.find().count()
        if sort_field:
            if sort_desc:
                q = q.sort(sort_field, -1)
            else:
                q = q.sort(sort_field)
        if page_size:
            q = q.limit(page_size)
            if page:
                q = q.skip(page * page_size)
        return count, q.find().all()

    def get_one(self, id):
        return self.model.m.get(_id=bson.ObjectId(id))

    def create_model(self, form):
        model = self.model.m.create(**form.data)
        model.m.insert()
        return model

    def update_model(self, form, model):
        parts = [
            getattr(self.model, fname).set(value)
            for fname, value in form.data.items()]
        spec = mql.and_(*parts)
        model.m.update(spec)

    def delete_model(self, model):
        model.m.remove()

    def is_valid_filter(self, flt):
        print 'validate', flt
        return False

    def scaffold_filters(self, name):
        fld = getattr(self.model, name)
        return filters.get_filters(fld)

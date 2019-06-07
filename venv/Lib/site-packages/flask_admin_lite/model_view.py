#-*-coding:utf-8-*-

from urlparse import urljoin
from jinja2 import Environment
from flask import Blueprint, abort, render_template, g, url_for, redirect, jsonify
from flask_paginate import Pagination
from .utils import prettify_classname


class BaseModelView(object):

    model_class = None
    columns = None

    CreateForm = None
    EditForm = None

    def __init__(self, name=None):
        self._name = name

    def get_pk_value(self, model):
        raise NotImplemented

    def get_one(self, id):
        raise NotImplemented

    def get_models(self, page, page_size=None):
        raise NotImplemented

    @property
    def name(self):
        return self._name or self.model_class.__name__

    @property
    def endpoint(self):
        return prettify_classname(self.model_class.__name__)

    @property
    def entry_url(self):
        return url_for('%s._list_view' % self.endpoint)

    def _list_view(self):
        attr_names = []
        column_names = []
        for column in self.columns:
            if isinstance(column, tuple):
                attr_name, column_name = column
            else:
                attr_name = column_name = column
            attr_names.append(attr_name)
            column_names.append(column_name)

        total, models = self.get_models(page=g.page)

        datas = []
        for model in models:
            data = {}
            for attr_name in attr_names:
                value = getattr(model, attr_name)
                if hasattr(self, 'render_' + attr_name):
                    tmpl = getattr(self, 'render_' + attr_name)(value)
                else:
                    tmpl = '{{' + attr_name + '}}'

                value = Environment().from_string(tmpl).render(**{
                    attr_name: value
                })
                data[attr_name] = value

            data['_pk_id'] = self.get_pk_value(model)
            datas.append(data)

        pagination = Pagination(page=g.page, per_page=self.page_size, total=total,
                                css_framework='bootstrap3')

        return render_template('list.html', total=total, models=datas,
                               attr_names=attr_names,
                               column_names=column_names,
                               pagination=pagination)

    def _create_view(self):
        form = self.CreateForm()
        if form.validate_on_submit():
            new_model = self.create_model(form)
            #TODO: check here
            return redirect(url_for('._list_view'))
        return render_template('edit.html', form=form)

    def _edit_view(self, id):
        model = self.get_one(id)
        if not model:
            return abort(404)
        form = self.EditForm(obj=model)
        if form.validate_on_submit():
            success = self.update_model(model, form)
            #TODO: check here
            return redirect(url_for('._list_view'))
        return render_template('edit.html', form=form)

    def _delete_view(self, id):
        model = self.get_one(id)
        if not model:
            return abort(404)
        ret = self.delete_model(model)
        return jsonify(success=ret)

    def create_blueprint(self, admin):
        url_prefix = urljoin(admin.url_prefix, self.endpoint)
        bp = Blueprint(self.endpoint, __name__, url_prefix=url_prefix,
                       template_folder='templates')

        bp.add_url_rule('/list', view_func=self._list_view, methods=['GET'])
        bp.add_url_rule('/create', view_func=self._create_view, methods=['GET', 'POST'])
        bp.add_url_rule('/<int:id>/edit', view_func=self._edit_view, methods=['GET', 'POST'])
        bp.add_url_rule('/<int:id>/delete', view_func=self._delete_view, methods=['POST'])

        @bp.before_request
        def _():
            g.view = self

        return bp

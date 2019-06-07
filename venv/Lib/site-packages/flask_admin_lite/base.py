#-*-coding:utf-8-*-

from flask import request, g, redirect, abort


class Admin(object):

    def __init__(self, app=None, name='Admin', url_prefix='/admin/'):
        self.name = name
        self.url_prefix = url_prefix
        self._views = []
        if app is not None:
            self.init_app(app)

    def add_view(self, view):
        self._views.append(view)
        if self.app is not None:
            self.app.register_blueprint(view.create_blueprint(self))

    def init_app(self, app):
        self.app = app
        self.add_index_view()
        self.app.before_request(self.before_request)
        for view in self._views:
            self.app.register_blueprint(view.create_blueprint(self))

    def index_view(self):
        if self._views:
            return redirect(self._views[0].entry_url)
        return abort(404)

    def add_index_view(self):
        self.app.add_url_rule(self.url_prefix, 'admin_index', self.index_view)

    def before_request(self):
        g.page = request.args.get('page', type=int, default=1)
        g.admin = self
        g.NAV_MENUS = [
            (view.name, view.entry_url) for view in self._views
        ]

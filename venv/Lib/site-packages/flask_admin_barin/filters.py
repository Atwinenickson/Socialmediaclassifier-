from flask_admin.model.filters import BaseFilter as _BaseFilter

from barin import schema as S


def get_filters(field):
    schema = field._schema
    if isinstance(schema, (S.Unicode, S.Number, S.DateTime)):
        res = [Eq, Lt, Gt, Le, Ge]
    elif isinstance(schema, (S.Binary, S.ObjectId)):
        res = [Eq]
    else:
        res = []
    return [cls(field, field._name) for cls in res]


class BaseFilter(_BaseFilter):

    def __init__(self, field, name, options=None, data_type=None):
        super(BaseFilter, self).__init__(name, options, data_type)
        self.field = field


class Eq(BaseFilter):

    def apply(self, query, value):
        return query.match(self.field == value)

    def operation(self):
        return '=='


class Lt(BaseFilter):

    def apply(self, query, value):
        return query.match(self.field < value)

    def operation(self):
        return '<'


class Gt(BaseFilter):

    def apply(self, query, value):
        return query.match(self.field > value)

    def operation(self):
        return '>'


class Le(BaseFilter):

    def apply(self, query, value):
        return query.match(self.field <= value)

    def operation(self):
        return '<='


class Ge(BaseFilter):

    def apply(self, query, value):
        return query.match(self.field >= value)

    def operation(self):
        return '>='

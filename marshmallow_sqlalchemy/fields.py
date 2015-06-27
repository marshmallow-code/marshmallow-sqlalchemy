# -*- coding: utf-8 -*-

from marshmallow import fields


def get_primary_column(model):
    columns = model.__mapper__.primary_key
    if len(columns) == 1:
        return columns[0]
    raise RuntimeError('Model {0!r} has multiple primary keys'.format(model))


class Related(fields.Field):

    @property
    def model(self):
        return self.parent.opts.model

    @property
    def related_model(self):
        return getattr(self.model, self.attribute or self.name).class_

    @property
    def related_column(self):
        return get_primary_column(self.related_model)

    @property
    def session(self):
        return self.parent.opts.sqla_session

    def _serialize(self, value, attr, obj):
        return getattr(value, self.related_column.key, None)

    def _deserialize(self, value):
        return self.session.query(
            self.related_model
        ).filter(
            self.related_column == value
        ).one()

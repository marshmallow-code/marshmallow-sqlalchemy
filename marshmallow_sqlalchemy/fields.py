# -*- coding: utf-8 -*-

from marshmallow import fields


def get_primary_column(model):
    """Get primary key column for a SQLAlchemy model.

    :param model: SQLAlchemy model class
    :raise: RuntimeError if model has multiple primary key columns
    """
    columns = model.__mapper__.primary_key
    if len(columns) == 1:
        return columns[0]
    raise RuntimeError('Model {0!r} has multiple primary keys'.format(model))


class Related(fields.Field):
    """Related data represented by a SQLAlchemy `relationship`. Must be attached
    to a :class:`Schema` class whose options includes a SQLAlchemy `model`, such
    as :class:`ModelSchema`.

    :param str column: Optional column name on related model. If not provided,
        the primary key of the related model will be used.
    """

    def __init__(self, column=None, **kwargs):
        super(Related, self).__init__(**kwargs)
        self.column = column

    @property
    def model(self):
        return self.parent.opts.model

    @property
    def related_model(self):
        return getattr(self.model, self.attribute or self.name).property.mapper.class_

    @property
    def related_column(self):
        if self.column:
            return self.related_model.__mapper__.columns[self.column]
        return get_primary_column(self.related_model)

    @property
    def session(self):
        return self.parent.session

    def _serialize(self, value, attr, obj):
        return getattr(value, self.related_column.key, None)

    def _deserialize(self, value, *args, **kwargs):
        return self.session.query(
            self.related_model
        ).filter(
            self.related_column == value
        ).one()

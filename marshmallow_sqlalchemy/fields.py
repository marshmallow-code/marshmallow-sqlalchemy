# -*- coding: utf-8 -*-

from marshmallow import fields


def get_primary_columns(model):
    """Get primary key columns for a SQLAlchemy model.

    :param model: SQLAlchemy model class
    """
    return model.__mapper__.primary_key

def ensure_list(value):
    return value if isinstance(value, list) else [value]

class Related(fields.Field):
    """Related data represented by a SQLAlchemy `relationship`. Must be attached
    to a :class:`Schema` class whose options includes a SQLAlchemy `model`, such
    as :class:`ModelSchema`.

    :param list columns: Optional column names on related model. If not provided,
        the primary key(s) of the related model will be used.
    """

    def __init__(self, column=None, **kwargs):
        super(Related, self).__init__(**kwargs)
        self.columns = ensure_list(column or [])

    @property
    def model(self):
        return self.parent.opts.model

    @property
    def related_model(self):
        return getattr(self.model, self.attribute or self.name).property.mapper.class_

    @property
    def related_columns(self):
        if self.columns:
            return [
                self.related_model.__mapper__.columns[column]
                for column in self.columns
            ]
        return get_primary_columns(self.related_model)

    @property
    def session(self):
        return self.parent.session

    def _serialize(self, value, attr, obj):
        ret = [
            getattr(value, column.key, None)
            for column in self.related_columns
        ]
        return ret if len(ret) > 1 else ret[0]

    def _deserialize(self, value, *args, **kwargs):
        return self.session.query(
            self.related_model
        ).filter_by(**{
            column.key: datum
            for column, datum in zip(self.related_columns, ensure_list(value))
        }).one()

# -*- coding: utf-8 -*-

from marshmallow import fields
from marshmallow.utils import is_iterable_but_not_string


def get_primary_columns(model):
    """Get primary key columns for a SQLAlchemy model.

    :param model: SQLAlchemy model class
    """
    return model.__mapper__.primary_key

def get_schema_for_field(field):
    if hasattr(field, 'root'):  # marshmallow>=2.1
        return field.root
    else:
        return field.parent

def ensure_list(value):
    return value if is_iterable_but_not_string(value) else [value]

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
        schema = get_schema_for_field(self)
        return schema.opts.model

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
        schema = get_schema_for_field(self)
        return schema.session

    def _serialize(self, value, attr, obj):
        ret = {
            column.key: getattr(value, column.key, None)
            for column in self.related_columns
        }
        return ret if len(ret) > 1 else list(ret.values())[0]

    def _deserialize(self, value, *args, **kwargs):
        if not isinstance(value, dict):
            if len(self.related_columns) != 1:
                raise ValueError(
                    'Could not deserialized related value {0!r}; expected a dictionary '
                    'with keys {1!r}'.format(
                        value,
                        [column.key for column in self.related_columns]
                    )
                )
            value = {self.related_columns[0].key: value}
        return self.session.query(
            self.related_model
        ).filter_by(**{
            column.key: value.get(column.key)
            for column in self.related_columns
        }).one()

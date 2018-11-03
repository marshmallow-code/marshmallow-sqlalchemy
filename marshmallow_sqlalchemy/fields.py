# -*- coding: utf-8 -*-

from marshmallow import fields
from marshmallow.utils import is_iterable_but_not_string

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.associationproxy import AssociationProxy

def get_primary_keys(model):
    """Get primary key properties for a SQLAlchemy model.

    :param model: SQLAlchemy model class
    """
    mapper = model.__mapper__
    return [
        mapper.get_property_by_column(column)
        for column in mapper.primary_key
    ]

def get_schema_for_field(field):
    if hasattr(field, 'root'):  # marshmallow>=2.1
        return field.root
    else:
        return field.parent

def ensure_list(value):
    return value if is_iterable_but_not_string(value) else [value]

class RelatedList(fields.List):

    def get_value(self, obj, attr, accessor=None):
        # Do not call `fields.List`'s get_value as it calls the container's
        # `get_value` if the container has `attribute`.
        # Instead call the `get_value` from the parent of `fields.List`
        # so the special handling is avoided.
        return super(fields.List, self).get_value(obj, attr, accessor=accessor)

class Related(fields.Field):
    """Related data represented by a SQLAlchemy `relationship`. Must be attached
    to a :class:`Schema` class whose options includes a SQLAlchemy `model`, such
    as :class:`ModelSchema`.

    :param list columns: Optional column names on related model. If not provided,
        the primary key(s) of the related model will be used.
    """

    default_error_messages = {
        'invalid': 'Could not deserialize related value {value!r}; '
                   'expected a dictionary with keys {keys!r}',
    }

    def __init__(self, column=None, **kwargs):
        super(Related, self).__init__(**kwargs)
        self.columns = ensure_list(column or [])

    @property
    def model(self):
        schema = get_schema_for_field(self)
        return schema.opts.model

    @property
    def related_model(self):
        model_attr = getattr(self.model, self.attribute or self.name)
        if isinstance(model_attr, AssociationProxy):
            model_attr = model_attr.remote_attr
        return model_attr.property.mapper.class_

    @property
    def related_keys(self):
        if self.columns:
            return [
                self.related_model.__mapper__.columns[column]
                for column in self.columns
            ]
        return get_primary_keys(self.related_model)

    @property
    def session(self):
        schema = get_schema_for_field(self)
        return schema.session

    def _serialize(self, value, attr, obj):
        ret = {
            prop.key: getattr(value, prop.key, None)
            for prop in self.related_keys
        }
        return ret if len(ret) > 1 else list(ret.values())[0]

    def _deserialize(self, value, *args, **kwargs):
        if not isinstance(value, dict):
            if len(self.related_keys) != 1:
                self.fail('invalid', value=value, keys=[prop.key for prop in self.related_keys])
            value = {self.related_keys[0].key: value}
        query = self.session.query(self.related_model)
        try:
            if self.columns:
                result = query.filter_by(**{
                    prop.key: value.get(prop.key)
                    for prop in self.related_keys
                }).one()
            else:
                # Use a faster path if the related key is the primary key.
                result = query.get([
                    value.get(prop.key) for prop in self.related_keys
                ])
                if result is None:
                    raise NoResultFound
        except NoResultFound:
            # The related-object DNE in the DB, but we still want to deserialize it
            # ...perhaps we want to add it to the DB later
            return self.related_model(**value)
        return result

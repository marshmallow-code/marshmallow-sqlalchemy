# -*- coding: utf-8 -*-

from sqlalchemy.sql.expression import or_, and_

from marshmallow import fields
from marshmallow.utils import is_iterable_but_not_string


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

class Related(fields.Field):
    """Related data represented by a SQLAlchemy `relationship`. Must be attached
    to a :class:`Schema` class whose options includes a SQLAlchemy `model`, such
    as :class:`ModelSchema`.

    :param list columns: Optional column names on related model. If not provided,
        the primary key(s) of the related model will be used.
    :param bool many: Whether the field is a collection of related objects.
    """

    def __init__(self, column=None, **kwargs):
        self.many = kwargs.get('many', False)
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
        if not self.many:
            value = [value]
        ret = []
        for item in value:
            related_keys = {
                prop.key: getattr(item, prop.key, None)
                for prop in self.related_keys
            }
            ret.append(related_keys if len(related_keys) > 1 else list(related_keys.values())[0])
        return ret if self.many else ret[0]

    def _deserialize(self, value, *args, **kwargs):
        if not self.many:
            value = [value]
        criteria = []
        for item in value:
            if not isinstance(item, dict):
                if len(self.related_keys) != 1:
                    raise ValueError(
                        'Could not deserialized related value {0!r}; expected a '
                        'dictionary with keys {1!r}'.format(
                            item, [prop.key for prop in self.related_keys]
                        )
                    )
                item = {self.related_keys[0].key: item}
            criteria.append(and_(*(prop.expression == item.get(prop.key)
                                   for prop in self.related_keys)))
        query = self.session.query(self.related_model).filter(or_(*criteria))
        return query.all() if self.many else query.one()

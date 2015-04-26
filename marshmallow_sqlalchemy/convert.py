# -*- coding: utf-8 -*-
import inspect

import marshmallow as ma
from marshmallow import validate, fields
from marshmallow.compat import text_type
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm.util import identity_key
import sqlalchemy as sa

from .exceptions import ModelConversionError

def get_pk_from_identity(obj):
    """Get primary key for `obj`. If `obj` has a compound primary key,
    return a string of keys separated by ``":"``.
    """
    _, key = identity_key(instance=obj)
    if len(key) == 1:
        return key[0]
    else:  # Compund primary key
        return ':'.join(text_type(x) for x in key)


class ModelConverter(object):
    """Class that converts a SQLAlchemy model into a dictionary of corresponding
    marshmallow `Fields <marshmallow.fields.Field>`.
    """

    SQLA_TYPE_MAPPING = {
        sa.String: fields.String,
        sa.Unicode: fields.String,
        sa.Boolean: fields.Boolean,
        sa.Unicode: fields.String,
        sa.Binary: fields.String,
        sa.Enum: fields.Field,
        sa.Numeric: fields.Decimal,
        sa.Float: fields.Decimal,
        sa.Date: fields.Date,
        postgresql.UUID: fields.UUID,
        postgresql.MACADDR: fields.String,
        postgresql.INET: fields.String,
    }

    DIRECTION_MAPPING = {
        'MANYTOONE': fields.QuerySelect,
        'MANYTOMANY': fields.QuerySelectList,
        'ONETOMANY': fields.QuerySelectList,
    }

    def fields_for_model(self, model, session=None, include_fk=False, keygetter=None, fields=None):
        result = {}
        for prop in model.__mapper__.iterate_properties:
            if fields and prop.key not in fields:
                continue
            if hasattr(prop, 'columns'):
                if not include_fk and prop.columns[0].foreign_keys:
                    continue
            field = self.property2field(prop, session=session, keygetter=keygetter)
            if field:
                result[prop.key] = field
        return result

    def property2field(self, prop, session=None, keygetter=None, instance=True):
        field_class = self._get_field_class_for_property(prop)
        if not instance:
            return field_class
        field_kwargs = self._get_field_kwargs_for_property(
            prop, session=session, keygetter=keygetter
        )
        return field_class(**field_kwargs)

    def _get_field_class_for_property(self, prop):
        if hasattr(prop, 'direction'):
            field_cls = self.DIRECTION_MAPPING[prop.direction.name]
        else:
            column = prop.columns[0]
            types = inspect.getmro(type(column.type))
            # First search for a field class from self.SQLA_TYPE_MAPPING
            for col_type in types:
                if col_type in self.SQLA_TYPE_MAPPING:
                    field_cls = self.SQLA_TYPE_MAPPING[col_type]
                    break
            else:
                # Try to find a field class based on the column's python_type
                if column.type.python_type in ma.Schema.TYPE_MAPPING:
                    field_cls = ma.Schema.TYPE_MAPPING[column.type.python_type]
                else:
                    raise ModelConversionError(
                        'Could not find field converter for {0} ({1}).'.format(prop.key, types[0]))
        return field_cls

    @staticmethod
    def _get_field_kwargs_for_property(prop, session=None, keygetter=None):
        kwargs = {
            'validate': []
        }
        if hasattr(prop, 'columns'):
            column = prop.columns[0]
            if column.nullable:
                kwargs['allow_none'] = True

            if hasattr(column.type, 'enums'):
                kwargs['validate'].append(validate.OneOf(choices=column.type.enums))

            # Add a length validator if a max length is set on the column
            if hasattr(column.type, 'length'):
                kwargs['validate'].append(validate.Length(max=column.type.length))

            if hasattr(column.type, 'scale'):
                kwargs['places'] = getattr(column.type, 'scale', None)

            # Primary keys are dump_only ("read-only")
            if getattr(column, 'primary_key', False):
                kwargs['dump_only'] = True
        if hasattr(prop, 'direction'):  # Relationship property
            # Get field class based on python type
            if not session:
                raise ModelConversionError(
                    'Cannot convert field {0}, need DB session.'.format(prop.key)
                )
            foreign_model = prop.mapper.class_
            nullable = True
            for pair in prop.local_remote_pairs:
                if not pair[0].nullable:
                    nullable = False
            kwargs.update({
                'allow_none': nullable,
                'query': lambda: session.query(foreign_model).all(),
                'keygetter': keygetter or get_pk_from_identity,
            })
        return kwargs


default_converter = ModelConverter()

fields_for_model = default_converter.fields_for_model
"""Generate a dict of field_name: `marshmallow.fields.Field` pairs for the
given model.

:param model: The SQLAlchemy model
:param Session session: SQLAlchemy session. Required if the model includes
    foreign key relationships.
:param bool include_fk: Whether to include foreign key fields from the
    output.
:return: dict of field_name: Field instance pairs
"""

property2field = default_converter.property2field
"""Convert a SQLAlchemy `Property` to a field instance or class.

:param Property prop: SQLAlchemy Property.
:param Session session: SQLALchemy session.
:param keygetter: See `marshmallow.fields.QuerySelect` for documenation on the
    keygetter parameter.
:param bool instance: If `True`, return  `Field` instance, computing relevant kwargs
    from the given property. If `False`, return the `Field` class.
:return: A `marshmallow.fields.Field` class or instance.
"""

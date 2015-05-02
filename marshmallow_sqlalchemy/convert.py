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
    return a string of keys separated by ``":"``. This is the default keygetter for
    used by `ModelSchema <marshmallow_sqlalchemy.ModelSchema>`.
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

    def property2field(self, prop, session=None, keygetter=None, instance=True, **kwargs):
        field_class = self._get_field_class_for_property(prop)
        if not instance:
            return field_class
        field_kwargs = self._get_field_kwargs_for_property(
            prop, session=session, keygetter=keygetter
        )
        field_kwargs.update(kwargs)
        return field_class(**field_kwargs)

    def column2field(self, column, instance=True, **kwargs):
        field_class = self._get_field_class_for_column(column)
        if not instance:
            return field_class
        field_kwargs = self.get_base_kwargs()
        self._add_column_kwargs(field_kwargs, column)
        field_kwargs.update(kwargs)
        return field_class(**field_kwargs)

    def _get_field_class_for_column(self, column):
        field_cls = None
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
                    'Could not find field column of type {0}.'.format(types[0]))
        return field_cls

    def _get_field_class_for_property(self, prop):
        if hasattr(prop, 'direction'):
            field_cls = self.DIRECTION_MAPPING[prop.direction.name]
        else:
            column = prop.columns[0]
            field_cls = self._get_field_class_for_column(column)
        return field_cls

    def _get_field_kwargs_for_property(self, prop, session=None, keygetter=None):
        kwargs = self.get_base_kwargs()
        if hasattr(prop, 'columns'):
            column = prop.columns[0]
            self._add_column_kwargs(kwargs, column)
        if hasattr(prop, 'direction'):  # Relationship property
            self._add_relationship_kwargs(kwargs, prop, session=session, keygetter=keygetter)
        if getattr(prop, 'doc', None):  # Useful for documentation generation
            kwargs['description'] = prop.doc
        return kwargs

    def _add_column_kwargs(self, kwargs, column):
        """Add keyword arguments to kwargs (in-place) based on the passed in
        `Column <sqlalchemy.schema.Column>`.
        """
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

    def _add_relationship_kwargs(self, kwargs, prop, session, keygetter=None):
        """Add keyword arguments to kwargs (in-place) based on the passed in
        relationship `Property`.
        """
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

    def get_base_kwargs(self):
        return {
            'validate': []
        }

default_converter = ModelConverter()

fields_for_model = default_converter.fields_for_model
"""Generate a dict of field_name: `marshmallow.fields.Field` pairs for the
given model.

:param model: The SQLAlchemy model
:param Session session: SQLAlchemy session. Required if the model includes
    foreign key relationships.
:param bool include_fk: Whether to include foreign key fields in the output.
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

column2field = default_converter.column2field
"""Convert a SQLAlchemy `Column <sqlalchemy.schema.Column>` to a field instance or class.

:param sqlalchemy.schema.Column column: SQLAlchemy Column.
:param bool instance: If `True`, return  `Field` instance, computing relevant kwargs
    from the given property. If `False`, return the `Field` class.
:return: A `marshmallow.fields.Field` class or instance.
"""

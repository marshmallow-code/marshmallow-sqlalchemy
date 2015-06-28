# -*- coding: utf-8 -*-
import inspect

import marshmallow as ma
from marshmallow.compat import with_metaclass

from .convert import ModelConverter


class SchemaOpts(ma.SchemaOpts):
    """Options class for `ModelSchema`.
    Adds the following options:

    - ``model``: The SQLAlchemy model to generate the `Schema` from (required).
    - ``sqla_session``: SQLAlchemy session (required).
    - ``model_converter``: `ModelConverter` class to use for converting the SQLAlchemy model to
        marshmallow fields.
    """

    def __init__(self, meta):
        super(SchemaOpts, self).__init__(meta)
        self.model = getattr(meta, 'model', None)
        self.sqla_session = getattr(meta, 'sqla_session', None)
        if self.model and not self.sqla_session:
            raise ValueError('SQLAlchemyModelSchema requires the "sqla_session" class Meta option')
        self.model_converter = getattr(meta, 'model_converter', ModelConverter)

class SchemaMeta(ma.schema.SchemaMeta):
    """Metaclass for `ModelSchema`."""

    # override SchemaMeta
    @classmethod
    def get_declared_fields(mcs, klass, *args, **kwargs):
        """Updates declared fields with fields converted from the SQLAlchemy model
        passed as the `model` class Meta option.
        """
        declared_fields = kwargs.get('dict_class', dict)()
        # inheriting from base classes
        for base in inspect.getmro(klass):
            opts = klass.opts
            if opts.model:
                Converter = opts.model_converter
                converter = Converter()
                declared_fields = converter.fields_for_model(
                    opts.model,
                    opts.sqla_session,
                    fields=opts.fields,
                )
                break
        base_fields = super(SchemaMeta, mcs).get_declared_fields(
            klass, *args, **kwargs
        )
        declared_fields.update(base_fields)
        return declared_fields


class ModelSchema(with_metaclass(SchemaMeta, ma.Schema)):
    """Base class for SQLAlchemy model-based Schemas.

    Example: ::

        from marshmallow_sqlalchemy import ModelSchema
        from mymodels import User, session

        class UserSchema(ModelSchema):
            class Meta:
                model = User
                sqla_session = session
    """
    OPTIONS_CLASS = SchemaOpts

    def make_object(self, data):
        return self.opts.model(**data)

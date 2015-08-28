# -*- coding: utf-8 -*-
import marshmallow as ma
from marshmallow.compat import with_metaclass

from .convert import ModelConverter


class SchemaOpts(ma.SchemaOpts):
    """Options class for `ModelSchema`.
    Adds the following options:

    - ``model``: The SQLAlchemy model to generate the `Schema` from (required).
    - ``sqla_session``: SQLAlchemy session to be used for deserialization. This is optional; you
        can also pass a session to the Schema's `load` method.
    - ``model_converter``: `ModelConverter` class to use for converting the SQLAlchemy model to
        marshmallow fields.
    """

    def __init__(self, meta):
        super(SchemaOpts, self).__init__(meta)
        self.model = getattr(meta, 'model', None)
        self.sqla_session = getattr(meta, 'sqla_session', None)
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
        opts = klass.opts
        if opts.model:
            Converter = opts.model_converter
            converter = Converter()
            declared_fields = converter.fields_for_model(
                opts.model,
                fields=opts.fields,
            )
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

        schema = UserSchema()

        user = schema.load({'name': 'Bill'}, session=session)
    """
    OPTIONS_CLASS = SchemaOpts

    def __init__(self, *args, **kwargs):
        session = kwargs.pop('session', None)
        super(ModelSchema, self).__init__(*args, **kwargs)
        self.session = session or self.opts.sqla_session

    def make_object(self, data):
        return self.opts.model(**data)

    def load(self, data, session=None, *args, **kwargs):
        self.session = session or self.session
        if not self.session:
            raise ValueError('Deserialization requires a session')
        return super(ModelSchema, self).load(data, *args, **kwargs)

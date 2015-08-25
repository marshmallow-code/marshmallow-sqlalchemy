# -*- coding: utf-8 -*-
import marshmallow as ma
from marshmallow.compat import with_metaclass

from .convert import ModelConverter
from .exceptions import ModelConversionError


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
                sqla_session = session
    """
    OPTIONS_CLASS = SchemaOpts

    def make_object(self, data):
        return self.opts.model(**data)


def setup_schema(Base, session):
    """Automatically setup Marshmallow schemas. Designed to trigger from
    SQLAlchemy's 'after_configured' event.

    Example: ::

        import sqlalchemy as sa
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import scoped_session, sessionmaker
        from sqlalchemy import event
        from sqlalchemy.orm import mapper
        from marshmallow_sqlalchemy import setup_schema

        engine = sa.create_engine('sqlite:///:memory:')
        session = scoped_session(sessionmaker(bind=engine))
        Base = declarative_base()

        class Author(Base):
            __tablename__ = 'authors'
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.String)

            def __repr__(self):
                return '<Author(name={self.name!r})>'.format(self=self)

        event.listen(mapper, 'after_configured', setup_schema(Base, session))

        Base.metadata.create_all(engine)

        author = Author(name='Chuck Paluhniuk')
        session.add(author)
        session.commit()

        author_schema = Author.__marshmallow__

        print author_schema.dump(author).data

    """
    def setup_schema_fn():
        for class_ in Base._decl_class_registry.values():
            if hasattr(class_, '__tablename__'):
                if class_.__name__.endswith('Schema'):
                    raise ModelConversionError(
                        "For safety, setup_schema can not be used when a"\
                        "Model class ends with 'Schema'"
                    )

                class Meta(object):
                    model = class_
                    sqla_session = session

                schema_class_name = '%sSchema' % class_.__name__

                schema_class = type(
                    schema_class_name,
                    (ModelSchema,),
                    {'Meta': Meta}
                )

                setattr(class_, '__marshmallow__', schema_class())

    return setup_schema_fn

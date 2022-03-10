**********************
marshmallow-sqlalchemy
**********************

Release v\ |version| (:ref:`Changelog <changelog>`)

`SQLAlchemy <http://www.sqlalchemy.org/>`_ integration with the  `marshmallow <https://marshmallow.readthedocs.io/en/latest/>`_ (de)serialization library.

Declare your models
===================

.. code-block:: python

    import sqlalchemy as sa
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref

    engine = sa.create_engine("sqlite:///:memory:")
    session = scoped_session(sessionmaker(bind=engine))
    Base = declarative_base()


    class Author(Base):
        __tablename__ = "authors"
        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.String, nullable=False)

        def __repr__(self):
            return "<Author(name={self.name!r})>".format(self=self)


    class Book(Base):
        __tablename__ = "books"
        id = sa.Column(sa.Integer, primary_key=True)
        title = sa.Column(sa.String)
        author_id = sa.Column(sa.Integer, sa.ForeignKey("authors.id"))
        author = relationship("Author", backref=backref("books"))


    Base.metadata.create_all(engine)

Generate marshmallow schemas
============================

.. code-block:: python

    from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field


    class AuthorSchema(SQLAlchemySchema):
        class Meta:
            model = Author
            load_instance = True  # Optional: deserialize to model instances

        id = auto_field()
        name = auto_field()
        books = auto_field()


    class BookSchema(SQLAlchemySchema):
        class Meta:
            model = Book
            load_instance = True

        id = auto_field()
        title = auto_field()
        author_id = auto_field()

You can automatically generate fields for a model's columns using `SQLAlchemyAutoSchema <marshmallow_sqlalchemy.SQLAlchemyAutoSchema>`.
The following schema classes are equivalent to the above.

.. code-block:: python

    from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


    class AuthorSchema(SQLAlchemyAutoSchema):
        class Meta:
            model = Author
            include_relationships = True
            load_instance = True


    class BookSchema(SQLAlchemyAutoSchema):
        class Meta:
            model = Book
            include_fk = True
            load_instance = True


Make sure to declare `Models` before instantiating `Schemas`. Otherwise `sqlalchemy.orm.configure_mappers() <https://docs.sqlalchemy.org/en/latest/orm/mapping_api.html>`_ will run too soon and fail.

.. note::

    Any `column_property` on the model that does not derive directly from `Column`
    (such as a mapped expression), will be detected and marked as `dump_only`.

    `hybrid_property` is not automatically handled at all, and would need to be
    explicitly declared as a field.

(De)serialize your data
=======================

.. code-block:: python

    author = Author(name="Chuck Paluhniuk")
    author_schema = AuthorSchema()
    book = Book(title="Fight Club", author=author)
    session.add(author)
    session.add(book)
    session.commit()

    dump_data = author_schema.dump(author)
    print(dump_data)
    # {'id': 1, 'name': 'Chuck Paluhniuk', 'books': [1]}

    load_data = author_schema.load(dump_data, session=session)
    print(load_data)
    # <Author(name='Chuck Paluhniuk')>


Get it now
==========
::

   pip install -U marshmallow-sqlalchemy

Requires Python >= 3.7, marshmallow >= 3.0.0, and SQLAlchemy >= 1.3.0.

Learn
=====

.. toctree::
    :maxdepth: 2

    recipes

API
===

.. toctree::
    :maxdepth: 2


    api_reference

Project Info
============

.. toctree::
   :maxdepth: 1

   changelog
   contributing
   authors
   license

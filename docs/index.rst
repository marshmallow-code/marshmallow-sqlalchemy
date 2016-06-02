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

    engine = sa.create_engine('sqlite:///:memory:')
    session = scoped_session(sessionmaker(bind=engine))
    Base = declarative_base()

    class Author(Base):
        __tablename__ = 'authors'
        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.String)

        def __repr__(self):
            return '<Author(name={self.name!r})>'.format(self=self)

    class Book(Base):
        __tablename__ = 'books'
        id = sa.Column(sa.Integer, primary_key=True)
        title = sa.Column(sa.String)
        author_id = sa.Column(sa.Integer, sa.ForeignKey('authors.id'))
        author = relationship("Author", backref=backref('books'))

    Base.metadata.create_all(engine)

Generate marshmallow schemas
============================

.. code-block:: python

    from marshmallow_sqlalchemy import ModelSchema

    class AuthorSchema(ModelSchema):
        class Meta:
            model = Author

    class BookSchema(ModelSchema):
        class Meta:
            model = Book
            # optionally attach a Session
            # to use for deserialization
            sqla_session = session

    author_schema = AuthorSchema()

(De)serialize your data
=======================

.. code-block:: python

    author = Author(name='Chuck Paluhniuk')
    book = Book(title='Fight Club', author=author)
    session.add(author)
    session.add(book)
    session.commit()

    dump_data = author_schema.dump(author).data
    # {'books': [123], 'id': 321, 'name': 'Chuck Paluhniuk'}

    author_schema.load(dump_data, session=session).data
    # <Author(name='Chuck Paluhniuk')>

Get it now
==========
::

   pip install -U marshmallow-sqlalchemy

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

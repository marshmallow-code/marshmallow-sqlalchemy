**********************
marshmallow-sqlalchemy
**********************

.. image:: https://badge.fury.io/py/marshmallow-sqlalchemy.png
    :target: http://badge.fury.io/py/marshmallow-sqlalchemy
    :alt: Latest version

.. image:: https://travis-ci.org/marshmallow-code/marshmallow-sqlalchemy.svg?branch=dev
    :target: https://travis-ci.org/marshmallow-code/marshmallow-sqlalchemy
    :alt: Travis-CI

Homepage: http://marshmallow-sqlalchemy.rtfd.org/

`SQLAlchemy <http://www.sqlalchemy.org/>`_ integration with the  `marshmallow <https://marshmallow.readthedocs.org/en/latest/>`_ (de)serialization library.

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
            sqla_session = session

    class BookSchema(ModelSchema):
        class Meta:
            model = Book
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

    author_schema.load(dump_data).data
    # <Author(name='Chuck Paluhniuk')>

Get it now
==========
::

   pip install -U marshmallow-sqlalchemy


Documentation
=============

Documentation is available at http://marshmallow-sqlalchemy.readthedocs.org/ .

Project Links
=============

- Docs: http://marshmallow-sqlalchemy.rtfd.org/
- Changelog: http://marshmallow-sqlalchemy.readthedocs.org/en/latest/changelog.html
- PyPI: https://pypi.python.org/pypi/marshmallow-sqlalchemy
- Issues: https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues

License
=======

MIT licensed. See the bundled `LICENSE <https://github.com/marshmallow-code/marshmallow-sqlalchemy/blob/dev/LICENSE>`_ file for more details.

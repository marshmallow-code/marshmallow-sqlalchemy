**********************
marshmallow-sqlalchemy
**********************

.. image:: https://travis-ci.org/marshmallow-code/marshmallow-sqlalchemy.svg?branch=dev
    :target: https://travis-ci.org/marshmallow-code/marshmallow-sqlalchemy


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

    from marshmallow_sqlalchemy import SQLAlchemyModelSchema as ModelSchema

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

    author_schema.dump(author).data
    # {'books': [123], 'id': 321, 'name': 'Chuck Paluhniuk'}


.. Documentation
.. -------------

.. Documentation is available at http://marshmallow-sqlalchemy.readthedocs.org/ .

License
-------

MIT licensed. See the bundled `LICENSE <https://github.com/marshmallow-code/marshmallow-sqlalchemy/blob/master/LICENSE>`_ file for more details.

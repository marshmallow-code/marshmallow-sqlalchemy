.. meta::
   :description:
        SQLALchemy integration with the marshmallow (de)serialization library.

**********************
marshmallow-sqlalchemy
**********************

`SQLAlchemy <http://www.sqlalchemy.org/>`_ integration with the  `marshmallow <https://marshmallow.readthedocs.io/en/latest/>`_ (de)serialization library.

Release v\ |version| (:ref:`Changelog <changelog>`)

----

Declare your models
===================

.. tab-set::

    .. tab-item:: SQLAlchemy 1.4
        :sync: sqla1

        .. code-block:: python

            import sqlalchemy as sa
            from sqlalchemy.orm import (
                DeclarativeBase,
                backref,
                relationship,
                sessionmaker,
            )

            from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

            engine = sa.create_engine("sqlite:///:memory:")
            Session = sessionmaker(engine)


            class Base(DeclarativeBase):
                pass


            class Author(Base):
                __tablename__ = "authors"
                id = sa.Column(sa.Integer, primary_key=True)
                name = sa.Column(sa.String, nullable=False)

                def __repr__(self):
                    return f"<Author(name={self.name!r})>"


            class Book(Base):
                __tablename__ = "books"
                id = sa.Column(sa.Integer, primary_key=True)
                title = sa.Column(sa.String)
                author_id = sa.Column(sa.Integer, sa.ForeignKey("authors.id"))
                author = relationship("Author", backref=backref("books"))

    .. tab-item:: SQLAlchemy 2
        :sync: sqla2

        .. code-block:: python

            import sqlalchemy as sa
            from sqlalchemy.orm import (
                DeclarativeBase,
                backref,
                relationship,
                sessionmaker,
                mapped_column,
                Mapped,
            )

            from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

            engine = sa.create_engine("sqlite:///:memory:")
            Session = sessionmaker(engine)


            class Base(DeclarativeBase):
                pass


            class Author(Base):
                __tablename__ = "authors"
                id: Mapped[int] = mapped_column(primary_key=True)
                name: Mapped[str] = mapped_column(nullable=False)

                def __repr__(self):
                    return f"<Author(name={self.name!r})>"


            class Book(Base):
                __tablename__ = "books"
                id: Mapped[int] = mapped_column(primary_key=True)
                title: Mapped[str] = mapped_column()
                author_id: Mapped[int] = mapped_column(sa.ForeignKey("authors.id"))
                author: Mapped["Author"] = relationship("Author", backref=backref("books"))


.. include:: ../README.rst
    :start-after: .. start elevator-pitch
    :end-before: .. end elevator-pitch

.. toctree::
    :maxdepth: 1
    :hidden:
    :titlesonly:

    Home <self>

Learn
=====

.. toctree::
    :caption: Learn
    :maxdepth: 2

    recipes

API reference
=============

.. toctree::
    :caption: API reference
    :maxdepth: 1

    api_reference

Project info
============

.. toctree::
    :caption: Project info
    :maxdepth: 1

    changelog
    contributing
    authors
    license

.. toctree::
    :hidden:
    :caption: Useful links

    marshmallow-sqlalchemy @ PyPI <https://pypi.org/project/marshmallow-sqlalchemy/>
    marshmallow-sqlalchemy @ GitHub <https://github.com/marshmallow-code/marshmallow-sqlalchemy/>
    Issue Tracker <https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues>

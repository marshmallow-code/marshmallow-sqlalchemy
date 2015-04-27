.. _recipes:

*******
Recipes
*******


Base Schema I
=============

A common pattern with `marshmallow` is to define a base `Schema <marshmallow.Schema>` class which has common configuration and behavior for your application's `Schemas`.

You may want to define a common session object, e.g. a `scoped_session <sqlalchemy.orm.scoping.scoped_session>` to use for all `Schemas <marshmallow.Schema>`.


.. code-block:: python

    # myproject/db.py
    import sqlalchemy as sa
    from sqlalchemy import orm

    Session = orm.scoped_session(orm.sessionmaker())
    Session.configure(bind=engine)

.. code-block:: python

    # myproject/schemas.py

    from marshmallow_sqlalchemy import ModelSchema

    from .db import Session

    class BaseSchema(ModelSchema):
        class Meta:
            sqla_session = Session


.. code-block:: python
    :emphasize-lines: 9

    # myproject/users/schemas.py

    from ..schemas import BaseSchema
    from .models import User

    class UserSchema(BaseSchema):

        # Inherit BaseSchema's options
        class Meta(BaseSchema.Meta):
            model = User

Base Schema II
==============

Here is an alternative way to define a BaseSchema class with a common ``Session`` object.

.. code-block:: python

    # myproject/schemas.py

    from marshmallow_sqlalchemy import SchemaOpts
    from .db import Session

    class BaseOpts(SchemaOpts):
        def __init__(self, meta):
            if not hasattr(meta, 'sql_session'):
                meta.sqla_session = Session
            super(BaseOpts, self).__init__(meta)

    class BaseSchema(ModelSchema):
        OPTIONS_CLASS = BaseOpts


This allows you to define class Meta options without having to subclass ``BaseSchema.Meta``.

.. code-block:: python
    :emphasize-lines: 8

    # myproject/users/schemas.py

    from ..schemas import BaseSchema
    from .models import User

    class UserSchema(BaseSchema):

        class Meta:
            model = User

Hyperlinking Relationships
==========================

By default, `ModelSchema <marshmallow_sqlalchemy.ModelSchema>` uses primary keys to represent relationships. You can override this
behavior by providing a custom ``keygetter``.

In a Hypermedia web API, you may choose to represent relationships as hyperlinks.

.. note::

    The following example uses `Flask <http://flask.pocoo.org/>`_ and `Flask-SQLAlchemy <http://flask-sqlalchemy.pocoo.org/>`_, but the pattern can easily be adapted for any web framework.

First, we require that models implement an ``absolute_url`` property.

.. code-block:: python
    :emphasize-lines: 8-10,18-20

    # myapp/models.py
    from .extensions import db

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        full_name = db.Column(db.String(255), nullable=True)

        @property
        def absolute_url(self):
            return url_for('user_detail', pk=self.id, _external=True)

    class Blog(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(255), nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        user = db.relationship(User, backref='blogs')

        @property
        def absolute_url(self):
            return url_for('blog_detail', pk=self.id, _external=True)


Then we define a base ``HyperlinkModelSchema`` that uses a custom ``keygetter``.

.. code-block:: python
    :emphasize-lines: 5,15,16

    # myapp/base.py
    from marshmallow_sqlalchemy import ModelSchema, SchemaOpts, get_pk_from_identity
    from .extensions import db

    def hyperlink_keygetter(obj):
        """Custom keygetter that uses the an object's
        absolute_url attribute as a unique key.
        """
        return obj.absolute_url

    class HyperlinkOpts(SchemaOpts):
        def __init__(self, meta):
            if not hasattr(meta, 'sql_session'):
                meta.sqla_session = db.session
            if not hasattr(meta, 'keygetter'):
                meta.keygetter = hyperlink_keygetter
            super(HyperlinkOpts, self).__init__(meta)

    class HyperlinkModelSchema(ModelSchema):
        OPTIONS_CLASS = HyperlinkOpts


We define our `Schemas <marshmallow.Schema>` as usual...

.. code-block:: python

    # myapp/schemas.py
    from .base import HyperlinkModelSchema

    class UserSchema(HyperlinkModelSchema):
        class Meta:
            model = User

    class BlogSchema(HyperlinkModelSchema):
        class Meta:
            model = Blog

    user_schema = UserSchema()
    blog_schema = BlogSchema()

...and use the schemas to serialize objects into hyperlinked responses.

.. code-block:: python
    :emphasize-lines: 9-13,19-23

    # myapp/views.py
    from flask import jsonify
    from .app import app

    @app.route('/users/<int:pk>')
    def user_detail(pk):
        user = User.query.get(pk)
        # ...
        # Example output:
        #   {'id': 42,
        #    'blogs': ['http://localhost/blogs/412'],
        #    'full_name': 'Monty Python'}
        return jsonify(user_schema.dump(user).data)

    @app.route('/blogs/<int:pk>')
    def blog_detail(pk):
        blog = Blog.query.get(pk)
        # ...
        # Example output:
        #   {'id': 412,
        #    'user': 'http://localhost/users/42',
        #    'title': 'Something completely different'}
        return jsonify(blog_schema.dump(blog).data)

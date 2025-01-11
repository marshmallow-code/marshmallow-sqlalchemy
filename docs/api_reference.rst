.. _api:

Top-level API
=============

.. Explicitly list which methods to document because :inherited-members: documents
.. all of Schema's methods, which we don't want
.. autoclass:: marshmallow_sqlalchemy.SQLAlchemySchema
    :members: load,get_instance,make_instance,validate,session,transient

.. autoclass:: marshmallow_sqlalchemy.SQLAlchemyAutoSchema
    :members: load,get_instance,make_instance,validate,session,transient

.. automodule:: marshmallow_sqlalchemy
    :members:
    :exclude-members: SQLAlchemySchema,SQLAlchemyAutoSchema

Fields
======

.. automodule:: marshmallow_sqlalchemy.fields
    :members:
    :exclude-members: get_value,default_error_messages,get_primary_keys

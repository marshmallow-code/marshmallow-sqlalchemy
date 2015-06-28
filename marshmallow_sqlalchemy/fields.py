# -*- coding: utf-8 -*-

import abc

import six
import sqlalchemy as sa
from marshmallow import fields


def get_primary_column(model):
    """Get primary key column for a SQLAlchemy model.

    :param model: SQLAlchemy model class
    :raise: RuntimeError if model has multiple primary key columns
    """
    columns = model.__mapper__.primary_key
    if len(columns) == 1:
        return columns[0]
    raise RuntimeError('Model {0!r} has multiple primary keys'.format(model))


class Related(fields.Field):
    """Related data represented by a SQLAlchemy `relationship`. Must be attached
    to a :class:`Schema` class whose options includes a SQLAlchemy `model`, such
    as :class:`ModelSchema`.
    """

    def __init__(self, column=None, **kwargs):
        super(Related, self).__init__(**kwargs)
        self.column = column

    @property
    def model(self):
        return self.parent.opts.model

    @property
    def related_model(self):
        return getattr(self.model, self.attribute or self.name).class_

    @property
    def related_column(self):
        if self.column:
            if isinstance(self.column, sa.Column):
                return self.column
            return self.model.__mapper__.columns[self.column]
        return get_primary_column(self.related_model)

    @property
    def session(self):
        return self.parent.opts.sqla_session

    def _serialize(self, value, attr, obj):
        return getattr(value, self.related_column.key, None)

    def _deserialize(self, value):
        return self.session.query(
            self.related_model
        ).filter(
            self.related_column == value
        ).one()


class HyperlinkRelated(six.with_metaclass(abc.ABCMeta, Related)):

    def _serialize(self, value, attr, obj):
        key = super(HyperlinkRelated, self)._serialize(value, attr, obj)
        return self._serialize_url(key, attr, obj)

    def _deserialize(self, value):
        key = self._deserialize_url(value)
        return super(HyperlinkRelated, self)._deserialize(key)

    @abc.abstractmethod
    def _serialize_url(self, value, attr, obj):
        pass

    @abc.abstractmethod
    def _deserialize_url(self, value):
        pass


class FlaskHyperlinkRelated(HyperlinkRelated):

    def __init__(self, app, endpoint, url_key='id', **kwargs):
        super(HyperlinkRelated, self).__init__(**kwargs)
        self.app = app
        self.endpoint = endpoint
        self.url_key = url_key

    @abc.abstractmethod
    def _serialize_url(self, value, attr, obj):
        from flask import url_for
        kwargs = {self.url_key: value}
        return url_for(self.endpoint, **kwargs)

    @abc.abstractmethod
    def _deserialize_url(self, value):
        endpoint, kwargs = self.adapter.match(value)
        if endpoint != self.endpoint:
            raise
        if self.url_key not in kwargs:
            raise
        return kwargs[self.url_key]

    @property
    def adapter(self):
        return self.app.url_map.bind('')

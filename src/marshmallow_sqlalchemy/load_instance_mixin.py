"""Mixin that adds model instance loading behavior.

.. warning::

    This module is treated as private API.
    Users should not need to use this module directly.
"""

from __future__ import annotations

import importlib.metadata
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Generic, TypeVar, Union, cast

import marshmallow as ma
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import ObjectDeletedError

from .fields import get_primary_keys

_LoadDataV3 = Union[Mapping[str, Any], Iterable[Mapping[str, Any]]]
_LoadDataV4 = Union[Mapping[str, Any], Sequence[Mapping[str, Any]]]
_LoadDataT = TypeVar("_LoadDataT", _LoadDataV3, _LoadDataV4)
_ModelType = TypeVar("_ModelType", bound=DeclarativeMeta)


def _cast_data(data):
    if int(importlib.metadata.version("marshmallow")[0]) >= 4:
        return cast(_LoadDataV4, data)
    return cast(_LoadDataV3, data)


class LoadInstanceMixin:
    class Opts:
        model: type[DeclarativeMeta] | None
        sqla_session: Session | None
        load_instance: bool
        transient: bool

        def __init__(self, meta, *args, **kwargs):
            super().__init__(meta, *args, **kwargs)
            self.model = getattr(meta, "model", None)
            self.sqla_session = getattr(meta, "sqla_session", None)
            self.load_instance = getattr(meta, "load_instance", False)
            self.transient = getattr(meta, "transient", False)

    class Schema(Generic[_ModelType]):
        opts: LoadInstanceMixin.Opts
        instance: _ModelType | None
        _session: Session | None
        _transient: bool | None
        _load_instance: bool

        @property
        def session(self) -> Session | None:
            """The SQLAlchemy session used to load models."""
            return self._session or self.opts.sqla_session

        @session.setter
        def session(self, session: Session) -> None:
            self._session = session

        @property
        def transient(self) -> bool:
            """Whether model instances are loaded in a transient state."""
            if self._transient is not None:
                return self._transient
            return self.opts.transient

        @transient.setter
        def transient(self, transient: bool) -> None:
            self._transient = transient

        def __init__(self, *args, **kwargs):
            self._session = kwargs.pop("session", None)
            self.instance = kwargs.pop("instance", None)
            self._transient = kwargs.pop("transient", None)
            self._load_instance = kwargs.pop("load_instance", self.opts.load_instance)
            super().__init__(*args, **kwargs)

        def get_instance(self, data) -> _ModelType | None:
            """Retrieve an existing record by primary key(s). If the schema instance
            is transient, return `None`.

            :param data: Serialized data to inform lookup.
            """
            if self.transient:
                return None
            model = cast(type[_ModelType], self.opts.model)
            props = get_primary_keys(model)
            filters = {prop.key: data.get(prop.key) for prop in props}
            if None not in filters.values():
                try:
                    return cast(Session, self.session).get(model, filters)
                except ObjectDeletedError:
                    return None
            return None

        @ma.post_load
        def make_instance(self, data, **kwargs) -> _ModelType:
            """Deserialize data to an instance of the model if self.load_instance is True.

            Update an existing row if specified in `self.instance` or loaded by primary
            key(s) in the data; else create a new row.

            :param data: Data to deserialize.
            """
            if not self._load_instance:
                return data
            instance = self.instance or self.get_instance(data)
            if instance is not None:
                for key, value in data.items():
                    setattr(instance, key, value)
                return instance
            kwargs, association_attrs = self._split_model_kwargs_association(data)
            ModelClass = cast(DeclarativeMeta, self.opts.model)
            instance = ModelClass(**kwargs)
            for attr, value in association_attrs.items():
                setattr(instance, attr, value)
            return instance

        def load(
            self,
            data: _LoadDataT,
            *,
            session: Session | None = None,
            instance: _ModelType | None = None,
            transient: bool = False,
            **kwargs,
        ) -> Any:
            """Deserialize data. If ``load_instance`` is set to `True`
            in the schema meta options, load the data as model instance(s).

            :param data: The data to deserialize.
            :param session: SQLAlchemy `session <sqlalchemy.orm.Session>`.
            :param instance: Existing model instance to modify.
            :param transient: If `True`, load transient model instance(s).
            :param kwargs: Same keyword arguments as `marshmallow.Schema.load`.
            """
            self._session = session or self._session
            self._transient = transient or self._transient
            if self._load_instance and not (self.transient or self.session):
                raise ValueError("Deserialization requires a session")
            self.instance = instance or self.instance
            try:
                return cast(ma.Schema, super()).load(_cast_data(data), **kwargs)
            finally:
                self.instance = None

        def validate(
            self,
            data: _LoadDataT,
            *,
            session: Session | None = None,
            **kwargs,
        ) -> dict[str, list[str]]:
            """Same as `marshmallow.Schema.validate` but allows passing a ``session``."""
            self._session = session or self._session
            if not (self.transient or self.session):
                raise ValueError("Validation requires a session")
            return cast(ma.Schema, super()).validate(_cast_data(data), **kwargs)

        def _split_model_kwargs_association(self, data):
            """Split serialized attrs to ensure association proxies are passed separately.

            This is necessary for Python < 3.6.0, as the order in which kwargs are passed
            is non-deterministic, and associations must be parsed by sqlalchemy after their
            intermediate relationship, unless their `creator` has been set.

            Ignore invalid keys at this point - behaviour for unknowns should be
            handled elsewhere.

            :param data: serialized dictionary of attrs to split on association_proxy.
            """
            association_attrs = {
                key: value
                for key, value in data.items()
                # association proxy
                if hasattr(getattr(self.opts.model, key, None), "remote_attr")
            }
            kwargs = {
                key: value
                for key, value in data.items()
                if (hasattr(self.opts.model, key) and key not in association_attrs)
            }
            return kwargs, association_attrs

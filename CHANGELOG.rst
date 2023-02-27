Changelog
---------

0.29.0 (2023-02-27)
+++++++++++++++++++

Features:

* Support SQLAlchemy 2.0 (:pr:`494`).
  Thanks :user:`dependabot` for the PR.
* Enable (in tests) and fix SQLAlchemy 2.0 compatibility warnings (:pr:`493`).

Bug fixes:

* Use mapper ``.attrs`` rather than ``.get_property`` and ``.iterate_properties``
  to ensure ``registry.configure`` is called (call removed in SQLAlchemy 2.0.2)
  (:issue:`487`).
  Thanks :user:`ddoyon92` for the PR.

Other changes:

* Drop support for SQLAlchemy 1.3, which is EOL (:pr:`493`).

0.28.2 (2023-02-23)
+++++++++++++++++++

Bug fixes:

* Use .scalar_subquery() for SQLAlchemy>1.4 to suppress a warning (:issue:`459`).
  Thanks :user:`indiVar0508` for the PR.

Other changes:

* Lock SQLAlchemy<2.0 in setup.py. SQLAlchemy 2.x is not supported (:pr:`486`).
* Test against Python 3.11 (:pr:`486`).

0.28.1 (2022-07-18)
+++++++++++++++++++

Bug fixes:

* Address ``DeprecationWarning`` re: usage of ``distutils`` (:pr:`435`).
 Thanks :user:`Tenzer` for the PR.

0.28.0 (2022-03-09)
+++++++++++++++++++

Features:

* Add support for generating fields from `column_property` (:issue:`97`).
  Thanks :user:`mrname` for the PR.

Other changes:

* Drop support for Python 3.6, which is EOL.
* Drop support for SQLAlchemy 1.2, which is EOL.

0.27.0 (2021-12-18)
+++++++++++++++++++

Features:

* Distribute type information per `PEP 561 <https://www.python.org/dev/peps/pep-0561/>`_ (:pr:`420`).
  Thanks :user:`bruceadams` for the PR.

Other changes:

* Test against Python 3.10 (:pr:`421`).

0.26.1 (2021-06-05)
+++++++++++++++++++

Bug fixes:

* Fix generating fields for ``postgreql.ARRAY`` columns (:issue:`392`).
 Thanks :user:`mjpieters` for the catch and patch.

0.26.0 (2021-05-26)
+++++++++++++++++++

Bug fixes:

* Unwrap proxied columns to handle models for subqueries (:issue:`383`).
  Thanks :user:`mjpieters` for the catch and patch
* Fix setting ``transient`` on a per-instance basis when the
  ``transient`` Meta option is set (:issue:`388`).
  Thanks again :user:`mjpieters`.

Other changes:

* *Backwards-incompatible*: Remove deprecated ``ModelSchema`` and ``TableSchema`` classes.


0.25.0 (2021-05-02)
+++++++++++++++++++

* Add ``load_instance`` as a parameter to `SQLAlchemySchema` and `SQLAlchemyAutoSchema` (:pr:`380`).
  Thanks :user:`mjpieters` for the PR.

0.24.3 (2021-04-26)
+++++++++++++++++++

* Fix deprecation warnings from marshmallow 3.10 and SQLAlchemy 1.4 (:pr:`369`).
  Thanks :user:`peterschutt` for the PR.

0.24.2 (2021-02-07)
+++++++++++++++++++

* ``auto_field`` supports ``association_proxy`` fields with local multiplicity
  (``uselist=True``) (:issue:`364`). Thanks :user:`Unix-Code`
  for the catch and patch.

0.24.1 (2020-11-20)
+++++++++++++++++++

* ``auto_field`` works with ``association_proxy`` (:issue:`338`).
  Thanks :user:`AbdealiJK`.

0.24.0 (2020-10-20)
+++++++++++++++++++

* *Backwards-incompatible*: Drop support for marshmallow 2.x, which is now EOL.
* Test against Python 3.9.

0.23.1 (2020-05-30)
+++++++++++++++++++

Bug fixes:

* Don't add no-op `Length` validator (:pr:`315`). Thanks :user:`taion` for the PR.

0.23.0 (2020-04-26)
+++++++++++++++++++

Bug fixes:

* Fix data keys when using ``Related`` with a ``Column`` that is named differently
  from its attribute (:issue:`299`). Thanks :user:`peterschutt` for the catch and patch.
* Fix bug that raised an exception when using the `ordered = True` option on a schema that has an `auto_field` (:issue:`306`).
  Thanks :user:`KwonL` for reporting and thanks :user:`peterschutt` for the PR.

0.22.3 (2020-03-01)
+++++++++++++++++++

Bug fixes:

* Fix ``DeprecationWarning`` getting raised even when user code does not use
  ``TableSchema`` or ``ModelSchema`` (:issue:`289`).
  Thanks :user:`5uper5hoot` for reporting.

0.22.2 (2020-02-09)
+++++++++++++++++++

Bug fixes:

* Avoid error when using ``SQLAlchemyAutoSchema``, ``ModelSchema``, or ``fields_for_model``
  with a model that has a ``SynonymProperty`` (:issue:`190`).
  Thanks :user:`TrilceAC` for reporting.
* ``auto_field`` and ``field_for`` work with ``SynonymProperty`` (:pr:`280`).

Other changes:

* Add hook in ``ModelConverter`` for changing field names based on SQLA columns and properties (:issue:`276`).
  Thanks :user:`davenquinn` for the suggestion and the PR.

0.22.1 (2020-02-09)
+++++++++++++++++++

Bug fixes:

* Fix behavior when passing ``table`` to ``auto_field`` (:pr:`277`).

0.22.0 (2020-02-09)
+++++++++++++++++++

Features:

* Add ``SQLAlchemySchema`` and ``SQLAlchemyAutoSchema``,
  which have an improved API for generating marshmallow fields
  and overriding their arguments via ``auto_field`` (:issue:`240`).
  Thanks :user:`taion` for the idea and original implementation.

.. code-block:: python

    # Before
    from marshmallow_sqlalchemy import ModelSchema, field_for

    from . import models


    class ArtistSchema(ModelSchema):
        class Meta:
            model = models.Artist

        id = field_for(models.Artist, "id", dump_only=True)
        created_at = field_for(models.Artist, "created_at", dump_only=True)


    # After
    from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

    from . import models


    class ArtistSchema(SQLAlchemyAutoSchema):
        class Meta:
            model = models.Artist

        id = auto_field(dump_only=True)
        created_at = auto_field(dump_only=True)

* Add ``load_instance`` option to configure deserialization to model instances (:issue:`193`, :issue:`270`).
* Add ``include_relationships`` option to configure generation of marshmallow fields for relationship properties (:issue:`98`).
  Thanks :user:`dusktreader` for the suggestion.

Deprecations:

* ``ModelSchema`` and ``TableSchema`` are deprecated,
  since ``SQLAlchemyAutoSchema`` has equivalent functionality.

.. code-block:: python

    # Before
    from marshmallow_sqlalchemy import ModelSchema, TableSchema

    from . import models


    class ArtistSchema(ModelSchema):
        class Meta:
            model = models.Artist


    class AlbumSchema(TableSchema):
        class Meta:
            table = models.Album.__table__


    # After
    from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

    from . import models


    class ArtistSchema(SQLAlchemyAutoSchema):
        class Meta:
            model = models.Artist
            include_relationships = True
            load_instance = True


    class AlbumSchema(SQLAlchemyAutoSchema):
        class Meta:
            table = models.Album.__table__

* Passing `info={"marshmallow": ...}` to SQLAlchemy columns is deprecated, as it is redundant with
  the ``auto_field`` functionality.

Other changes:

* *Backwards-incompatible*: ``fields_for_model`` does not include relationships by default.
  Use ``fields_for_model(..., include_relationships=True)`` to preserve the old behavior.

0.21.0 (2019-12-04)
+++++++++++++++++++

* Add support for ``postgresql.OID`` type (:pr:`262`).
  Thanks :user:`petrus-v` for the PR.
* Remove imprecise Python 3 classifier from PyPI metadata (:pr:`255`).
  Thanks :user:`ecederstrand`.

0.20.0 (2019-12-01)
+++++++++++++++++++

* Add support for ``mysql.DATETIME`` and ``mysql.INTEGER`` type (:issue:`204`).
* Add support for ``postgresql.CIDR`` type (:issue:`183`).
* Add support for ``postgresql.DATE`` and ``postgresql.TIME`` type.

Thanks :user:`evelyn9191` for the PR.

0.19.0 (2019-09-05)
+++++++++++++++++++

* Drop support for Python 2.7 and 3.5 (:issue:`241`).
* Drop support for marshmallow<2.15.2.
* Only support sqlalchemy>=1.2.0.

0.18.0 (2019-09-05)
+++++++++++++++++++

Features:

* ``marshmallow_sqlalchemy.fields.Nested`` propagates the value of ``transient`` on the call to ``load`` (:issue:`177`, :issue:`206`).
  Thanks :user:`leonidumanskiy` for reporting.

Note: This is the last release to support Python 2.7 and 3.5.

0.17.2 (2019-08-31)
+++++++++++++++++++

Bug fixes:

* Fix error handling when passing an invalid type to ``Related`` (:issue:`223`).
  Thanks :user:`heckad` for reporting.
* Address ``DeprecationWarning`` raised when using ``Related`` with marshmallow 3 (:pr:`243`).

0.17.1 (2019-08-31)
+++++++++++++++++++

Bug fixes:

* Add ``marshmallow_sqlalchemy.fields.Nested`` field that inherits its session from its schema. This fixes a bug where an exception was raised when using ``Nested`` within a ``ModelSchema`` (:issue:`67`).
  Thanks :user:`nickw444` for reporting and thanks :user:`samueljsb` for the PR.

User code should be updated to use marshmallow-sqlalchemy's ``Nested`` instead of ``marshmallow.fields.Nested``.

.. code-block:: python

    # Before
    from marshmallow import fields
    from marshmallow_sqlalchemy import ModelSchema


    class ArtistSchema(ModelSchema):
        class Meta:
            model = models.Artist


    class AlbumSchema(ModelSchema):
        class Meta:
            model = models.Album

        artist = fields.Nested(ArtistSchema)


    # After
    from marshmallow import fields
    from marshmallow_sqlalchemy import ModelSchema
    from marshmallow_sqlalchemy.fields import Nested


    class ArtistSchema(ModelSchema):
        class Meta:
            model = models.Artist


    class AlbumSchema(ModelSchema):
        class Meta:
            model = models.Album

        artist = Nested(ArtistSchema)

0.17.0 (2019-06-22)
+++++++++++++++++++

Features:

* Add support for ``postgresql.MONEY`` type (:issue:`218`). Thanks :user:`heckad` for the PR.

0.16.4 (2019-06-15)
+++++++++++++++++++

Bug fixes:

* Compatibility with marshmallow 3.0.0rc7. Thanks :user:`heckad` for the catch and patch.

0.16.3 (2019-05-05)
+++++++++++++++++++

Bug fixes:

* Compatibility with marshmallow 3.0.0rc6.

0.16.2 (2019-04-10)
+++++++++++++++++++

Bug fixes:

* Prevent ValueError when using the ``exclude`` class Meta option with
  ``TableSchema`` (:pr:`202`).

0.16.1 (2019-03-11)
+++++++++++++++++++

Bug fixes:

* Fix compatibility with SQLAlchemy 1.3 (:issue:`185`).

0.16.0 (2019-02-03)
+++++++++++++++++++

Features:

* Add support for deserializing transient objects (:issue:`62`).
  Thanks :user:`jacksmith15` for the PR.

0.15.0 (2018-11-05)
+++++++++++++++++++

Features:

* Add ``ModelConverter._should_exclude_field`` hook (:pr:`139`).
  Thanks :user:`jeanphix` for the PR.
* Allow field ``kwargs`` to be overriden by passing
  ``info['marshmallow']`` to column properties (:issue:`21`).
  Thanks :user:`dpwrussell` for the suggestion and PR.
  Thanks :user:`jeanphix` for the final implementation.

0.14.2 (2018-11-03)
+++++++++++++++++++

Bug fixes:

- Fix behavior of ``Related`` field (:issue:`150`). Thanks :user:`zezic`
  for reporting and thanks :user:`AbdealiJK` for the PR.
- ``Related`` now works with ``AssociationProxy`` fields (:issue:`151`).
  Thanks :user:`AbdealiJK` for the catch and patch.

Other changes:

- Test against Python 3.7.
- Bring development environment in line with marshmallow.

0.14.1 (2018-07-19)
+++++++++++++++++++

Bug fixes:

- Fix behavior of ``exclude`` with marshmallow 3.0 (:issue:`131`).
  Thanks :user:`yaheath` for reporting and thanks :user:`deckar01` for
  the fix.

0.14.0 (2018-05-28)
+++++++++++++++++++

Features:

- Make ``ModelSchema.session`` a property, which allows session to be
  retrieved from ``context`` (:issue:`129`). Thanks :user:`gtxm`.

Other changes:

- Drop official support for Python 3.4. Python>=3.5 and Python 2.7 are supported.

0.13.2 (2017-10-23)
+++++++++++++++++++

Bug fixes:

- Unset ``instance`` attribute when an error occurs during a ``load``
  call (:issue:`114`). Thanks :user:`vgavro` for the catch and patch.

0.13.1 (2017-04-06)
+++++++++++++++++++

Bug fixes:

- Prevent unnecessary queries when using the `fields.Related` (:issue:`106`). Thanks :user:`xarg` for reporting and thanks :user:`jmuhlich` for the PR.

0.13.0 (2017-03-12)
+++++++++++++++++++

Features:

- Invalid inputs for compound primary keys raise a ``ValidationError`` when deserializing a scalar value (:issue:`103`). Thanks :user:`YuriHeupa` for the PR.

Bug fixes:

- Fix compatibility with marshmallow>=3.x.

0.12.1 (2017-01-05)
+++++++++++++++++++

Bug fixes:

- Reset ``ModelSchema.instance`` after each ``load`` call, allowing schema instances to be reused (:issue:`78`). Thanks :user:`georgexsh` for reporting.

Other changes:

- Test against Python 3.6.

0.12.0 (2016-10-08)
+++++++++++++++++++

Features:

- Add support for TypeDecorator-based types (:issue:`83`). Thanks :user:`frol`.

Bug fixes:

- Fix bug that caused a validation errors for custom column types that have the ``python_type`` of ``uuid.UUID`` (:issue:`54`). Thanks :user:`wkevina` and thanks :user:`kelvinhammond` for the fix.

Other changes:

- Drop official support for Python 3.3. Python>=3.4 and Python 2.7 are supported.

0.11.0 (2016-10-01)
+++++++++++++++++++

Features:

- Allow overriding field class returned by ``field_for`` by adding the ``field_class`` param (:issue:`81`). Thanks :user:`cancan101`.

0.10.0 (2016-08-14)
+++++++++++++++++++

Features:

- Support for SQLAlchemy JSON type (in SQLAlchemy>=1.1) (:issue:`74`). Thanks :user:`ewittle` for the PR.

0.9.0 (2016-07-02)
++++++++++++++++++

Features:

- Enable deserialization of many-to-one nested objects that do not exist in the database (:issue:`69`). Thanks :user:`seanharr11` for the PR.

Bug fixes:

- Depend on SQLAlchemy>=0.9.7, since marshmallow-sqlalchemy uses ``sqlalchemy.dialects.postgresql.JSONB`` (:issue:`65`). Thanks :user:`alejom99` for reporting.

0.8.1 (2016-02-21)
++++++++++++++++++

Bug fixes:

- ``ModelSchema`` and ``TableSchema`` respect field order if the ``ordered=True`` class Meta option is set (:issue:`52`). Thanks :user:`jeffwidman` for reporting and :user:`jmcarp` for the patch.
- Declared fields are not introspected in order to support, e.g. ``column_property`` (:issue:`57`). Thanks :user:`jmcarp`.

0.8.0 (2015-12-28)
++++++++++++++++++

Features:

- ``ModelSchema`` and ``TableSchema`` will respect the ``TYPE_MAPPING`` class variable of Schema subclasses when converting ``Columns`` to ``Fields`` (:issue:`42`). Thanks :user:`dwieeb` for the suggestion.

0.7.1 (2015-12-13)
++++++++++++++++++

Bug fixes:

- Don't make marshmallow fields required for non-nullable columns if a column has a default value or autoincrements (:issue:`47`). Thanks :user:`jmcarp` for the fix. Thanks :user:`AdrielVelazquez` for reporting.

0.7.0 (2015-12-07)
++++++++++++++++++

Features:

- Add ``include_fk`` class Meta option (:issue:`36`). Thanks :user:`jmcarp`.
- Non-nullable columns will generated required marshmallow Fields (:issue:`40`). Thanks :user:`jmcarp`.
- Improve support for MySQL BIT field (:issue:`41`). Thanks :user:`rudaporto`.
- *Backwards-incompatible*: Remove ``fields.get_primary_columns`` in favor of ``fields.get_primary_keys``.
- *Backwards-incompatible*: Remove ``Related.related_columns`` in favor of ``fields.related_keys``.

Bug fixes:

- Fix serializing relationships when using non-default column names (:issue:`44`). Thanks :user:`jmcarp` for the fix. Thanks :user:`repole` for the bug report.

0.6.0 (2015-09-29)
++++++++++++++++++

Features:

- Support for compound primary keys. Thanks :user:`jmcarp`.

Other changes:

- Supports marshmallow>=2.0.0.

0.5.0 (2015-09-27)
++++++++++++++++++

- Add ``instance`` argument to ``ModelSchema`` constructor and ``ModelSchema.load`` which allows for updating existing DB rows (:issue:`26`). Thanks :user:`sssilver` for reporting and :user:`jmcarp` for the patch.
- Don't autogenerate fields that are in ``Meta.exclude`` (:issue:`27`). Thanks :user:`jmcarp`.
- Raise ``ModelConversionError`` if converting properties whose column don't define a ``python_type``. Thanks :user:`jmcarp`.
-  *Backwards-incompatible*: ``ModelSchema.make_object`` is removed in favor of decorated ``make_instance`` method for compatibility with marshmallow>=2.0.0rc2.

0.4.1 (2015-09-13)
++++++++++++++++++

Bug fixes:

- Now compatible with marshmallow>=2.0.0rc1.
- Correctly pass keyword arguments from ``field_for`` to generated ``List`` fields (:issue:`25`). Thanks :user:`sssilver` for reporting.


0.4.0 (2015-09-03)
++++++++++++++++++

Features:

- Add ``TableSchema`` for generating ``Schemas`` from tables (:issue:`4`). Thanks :user:`jmcarp`.

Bug fixes:

- Allow ``session`` to be passed to ``ModelSchema.validate``, since it requires it. Thanks :user:`dpwrussell`.
- When serializing, don't skip overriden fields that are part of a polymorphic hierarchy (:issue:`18`). Thanks again :user:`dpwrussell`.

Support:

- Docs: Add new recipe for automatic generation of schemas. Thanks :user:`dpwrussell`.

0.3.0 (2015-08-27)
++++++++++++++++++

Features:

- *Backwards-incompatible*: Relationships are (de)serialized by a new, more efficient ``Related`` column (:issue:`7`). Thanks :user:`jmcarp`.
- Improve support for MySQL types (:issue:`1`). Thanks :user:`rmackinnon`.
- Improve support for Postgres ARRAY types (:issue:`6`). Thanks :user:`jmcarp`.
- ``ModelSchema`` no longer requires the ``sqla_session`` class Meta option. A ``Session`` can be passed to the constructor or to the ``ModelSchema.load`` method (:issue:`11`). Thanks :user:`dtheodor` for the suggestion.

Bug fixes:

- Null foreign keys are serialized correctly as ``None`` (:issue:`8`). Thanks :user:`mitchej123`.
- Properly handle a relationship specifies ``uselist=False`` (:issue:`#17`). Thanks :user:`dpwrussell`.

0.2.0 (2015-05-03)
++++++++++++++++++

Features:

- Add ``field_for`` function for generating marshmallow Fields from SQLAlchemy mapped class properties.

Support:

- Docs: Add "Overriding generated fields" section to "Recipes".

0.1.1 (2015-05-02)
++++++++++++++++++

Bug fixes:

- Fix ``keygetter`` class Meta option.

0.1.0 (2015-04-28)
++++++++++++++++++

- First release.

Changelog
---------

0.21.0 (unreleased)
+++++++++++++++++++

* Add support for ``postgresql.OID`` type (:pr:`262`).
  Thanks :user:`petrus-v` for the PR.

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

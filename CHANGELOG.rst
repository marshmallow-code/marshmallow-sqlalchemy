Changelog
---------

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

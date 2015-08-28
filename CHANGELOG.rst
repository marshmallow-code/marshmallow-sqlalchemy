Changelog
---------

0.3.0 (unreleased)
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

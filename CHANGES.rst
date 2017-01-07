==========
Change log
==========


2.10 (unreleased)
=================

Other
-----

- Update most libraries needed for the address book to their newest versions.


2.9 (2017-01-06)
================

Features
--------

- Add view `@@inspector` to see internals of the rendered view or object. This
  view can only be accessed as global administrator (the one who is able to
  create new address books).

Bugs
----

- Fix configuration error which might prevent the start-up in 2.8.

Other
-----

- Rework roles management for administrators to allow in future permissions
  which administrators do not get by default.

- Bring test coverage including branches to 100 %.


2.8 (2016-08-28)
================

Features
--------

- Store timestamp of last log-in and render it in the principals list.

2.7.1 (2016-06-26)
==================

- Update to an `icemac.ab.locales` version which has complete translations
  for all address book and calendar features.


2.7 (2016-06-25)
================

Features
--------

- Render field descriptions (resp. notes of user defined fields) as hint text
  below the widget in the form.

- Allow to select a default time zone in the address book's edit form. It is
  used for all users who do not have set their own time zone in the
  preferences.

- Whitespace gets stripped from both ends of entered text values. Excluded are
  only the text fields in the `update` search result handler.

Other
-----

- Update most libraries needed for the address book to their newest versions.

- Get rid of dependency on ``classproperty``.

2.6.4 (2016-04-16)
==================

- Enable versioning in `fanstatic` so the no force-reload is needed to get the
  new CSS file versions.

2.6.3 (2016-04-16)
==================

- Allow to run `icemac.ab.calendar` 1.8 with this address book version.


2.6.2 (2016-03-12)
==================

- Render more form error messages in red.


2.6.1 (2016-03-08)
==================

- Fix backup and restore scripts which where broken due to updating to ZODB
  4.x.


2.6 (2016-03-05)
================

Features
--------

- Add javascript date picker to date fields.

- iCal export of birth dates now includes birth year, too.

- Add new `time` data type for user defined fields.

- Render time picker for `time` fields.

Fixes
-----

- Store ``datetime`` values in UTC.

Other
-----

- Update most libraries needed for address book to newest versions.

- No longer depend on ZTK but build up our own list.

- Lint JavaScript files.

- Rewrite tests to use py.test.

- Update Selenium tests to Webdriver.

- Move some functionality only needed in `icemac.ab.importer` there.

- Drop `.utils.site()` in favour of `zope.component.hooks.site()`.


Previous Versions
=================

See `OLD_CHANGES.rst`_.

.. _`OLD_CHANGES.rst` : https://bitbucket.org/icemac/icemac.addressbook/src/tip/OLD_CHANGES.rst

==========
 Download
==========

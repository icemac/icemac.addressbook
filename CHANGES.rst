==========
Change log
==========

2.6.4 (unreleased)
==================

- Nothing changed yet.


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

2.5.2 (2014-12-18)
==================

- Fix multi selects broken in Internet Explorer 10 by updating to `z3c.form
  3.2.1`.


2.5.1 (2014-07-03)
==================

- Fix persistent view names containing ``@@`` which was doubled since 2.5.0.


2.5.0 (2014-07-01)
==================

Features
--------

- Display roles in user list.

Fixes
-----

- Fix highlighting in the main menu: tabs are highlighted even if moving on
  to subviews.

Other
-----

- Updated to run on `Zope Toolkit 1.1.6`_.

- Add `py.test` to run the tests.

- Automatically add ``@@`` in front of the view names.

.. _`Zope Toolkit 1.1.6`: http://docs.zope.org/zopetoolkit/releases/overview-1.1.6.html



2.4.1 (2014-03-08)
==================

Fixes
-----

- Fix brown bag release 2.4.0: The migration of the ZODB from a previous
  version was broken.

- No longer require `rsync` to be installed for migrations.

- No longer copy the whole backup history when migrating but make a fresh
  backup.


2.4.0 (2014-03-07)
==================

Features
--------

- Added search result handler which exports birthdates als iCalendar file.

- Added export ability for a single person currently only exporting person's
  birthdate as iCalendar file.


Other
-----

- Updated most other packages (outside ZTK) needed for address book to
  newest versions.


Previous Versions
=================

See `OLD_CHANGES.rst`_.

.. _`OLD_CHANGES.rst` : https://bitbucket.org/icemac/icemac.addressbook/src/tip/OLD_CHANGES.rst

==========
 Download
==========

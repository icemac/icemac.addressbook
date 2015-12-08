==========
Change log
==========

2.6.0 (unreleased)
==================

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


2.3.0 (2014-02-08)
==================

- Refactoring: Add option to add a query string to the URL in `url` method.

- Refactoring: Allow additional packages to register their roles to be
  handled like `Editor` or `Visitor` thus allowing them to change their
  username and/or password.


Previous Versions
=================

See `OLD_CHANGES.rst`_.

.. _`OLD_CHANGES.rst` : https://bitbucket.org/icemac/icemac.addressbook/src/tip/OLD_CHANGES.rst

==========
 Download
==========

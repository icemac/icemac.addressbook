==========
Change log
==========

2.4.1 (unreleased)
==================

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


2.2.0 (2014-01-02)
==================

- Refactoring: Added `session` property to `BaseView` to ease session access.


Previous Versions
=================

See ``OLD_CHANGES.rst`` inside the package.

==========
 Download
==========

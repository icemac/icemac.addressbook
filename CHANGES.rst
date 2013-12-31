==========
Change log
==========

2.1.0 (unreleased)
==================

- Feature: Add ability to set start page for all users in master data
  section. It is shown after a user has logged in. (It no longer needs to be
  the welcome page introduced in version 1.10.)


2.0.1 (2013-12-08)
==================

- Update used buildout recipe `z3c.recipe.staticlxml` to a version
  compatible with some 64 bit Linux like Suse Linux.


2.0.0 (2013-11-09)
==================

Features
--------

- Put focus on first input field of form after loading the form.

- FavIcon can now be selected in address book section of master data.

- Add confirmation before cloning a person.

Bugfixes
--------

- The year in dates now have to be entered with 4 digits allowing to enter
  birthdates before 1930. (Merge from 1.10 branch.)

- Show metadata for entity field order list.

- Show only most common time zones in prefereces for select.

Other
-----

- Changed required Python to version 2.7.x, no longer supporting Python 2.6.

- Updated most other packages (outside ZTK) needed for address book to
  newest versions.


1.10.2 (2013-07-06)
===================

- Update to `zc.buildout` 1.7.1.

- Downgrade ``bootstrap.py`` to the version of `zc.buildout` 1.7.1 so
  initial bootstrap does not fail. This problem was introduced in version 1.10.1.


1.10.1 (2013-06-25)
===================

- Update ``bootstrap.py`` to current version so updating an older instance
  does not fail.


1.10.0 (2013-06-21)
===================

Features
--------

- Added welcome page displayed after login. So additional packages might
  provide roles which do not allow to access the persons in the address
  book.

- Added ability in user preferences to set current time zone. Datetimes,
  e. g. creation date, modification date and user defined fields of type
  datetime, are converted to the selected time zone. Default is UTC.

- Added JavaScript calendar widget to datetime fields.

- Added number of displayed persons in search result handler which displays
  the names of the selected persons (new in 1.9.0).

- Now displays the name of the address book in HTML title tag and as
  headline inside the application.

- Moved link to edit form of address book from tabs to master data.

- Added checkbox in search result table to deselect all entries.

Other
-----

- Moved source code to: https://bitbucket.org/icemac/icemac.addressbook

- Updated to run on `Zope Toolkit 1.1.5`_.

- Updated most other packages (outside ZTK) needed for address book to
  newest versions.

- Simplified and streamlined test layers.

.. _`Zope Toolkit 1.1.5`: http://docs.zope.org/zopetoolkit/releases/overview-1.1.5.html


Previous Versions
=================

See ``OLD_CHANGES.rst`` inside the package.

==========
 Download
==========

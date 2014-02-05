==========
Change log
==========

2.3.0 (unreleased)
==================

- Refactoring: Add option to add a query string to the URL in `url` method.


2.2.0 (2014-01-02)
==================

- Refactoring: Added `session` property to `BaseView` to ease session access.


2.1.0 (2013-12-31)
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

Previous Versions
=================

See ``OLD_CHANGES.rst`` inside the package.

==========
 Download
==========

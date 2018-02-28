==========
Change log
==========


6.0 (unreleased)
================

Backward incompatible changes
-----------------------------

- Add a `schema_name` index to distinguish between entities in the catalog.

Bug fixes
---------

- Fix the breadcrumbs on the about page and the logout page.

Other
-----

- Move the documentation from
  https://bitbucket.org/icemac/icemac.addressbook/wiki/ to
  https://icemacaddressbook.readthedocs.io

- Update most libraries needed for the address book to their newest versions.


5.0.2 (2017-12-27)
==================

- The install process seems to have to access PyPI using HTTPS nowadays.


5.0.1 (2017-12-27)
==================

- Fix the install scripts to only depend on the standard library.


5.0 (2017-12-26)
================

Backward incompatible changes
-----------------------------

- Use select2 JavaScript library to nicely render the select fields.

Features
--------

- Render breadcrumbs to be able to access the parent object.

Other
-----

- Update most libraries needed for the address book to their newest versions.

- Move ``.conftest.tmpfile()`` to ``.fixtures.tmpfile()`` for reuse.

- Make some Python 3 preparations as suggested by `pylint --py3k -d W1618`.
  (No checks for future-absolute-imports as relative imports are not used
  here.)

- Change `zope.interface.implements[Only]` and `zope.component.adapts` to
  class decorators.

- Also release as wheel.


4.1.1 (2017-05-18)
==================

- Fix broken forms when using newlines in the description of user defined
  fields.


4.1 (2017-05-16)
================

Features
--------

- Render the name of the logged-in user as a link to the edit form of his
  personal data.

Other changes
-------------

- Style a secondary menu alike the main menu.

- Update to a version of `icemac.recurrence` which fixed a bug in the
  computation of monthly recurring events on DST borders.

- Update most libraries needed for the address book to their newest versions.


4.0 (2017-04-08)
================

Backward incompatible changes
-----------------------------

- Update the tests and test infrastructure to `zope.testbrowser >= 5.x`.
  This version is no longer built on `mechanize` but on `WebTest`. This
  requires some changes as the underlying framework is not completely
  abstracted in `zope.testbrowser`.

- Refactor ``.testing.Webdriver`` to be able to implement the
  `Page Object Design Pattern`_. ``.testing.Webdriver.login()`` no longer
  returns a `selenium` object. Page objects have to be registered using
  ``.testing.Webdriver.attach()``.

- Require the second argument (``path``) of ``.testing.Webdriver.login()`` to
  reduce the overhead of the selenium login.


.. _`Page Object Design Pattern` : http://www.seleniumhq.org/docs/06_test_design_considerations.jsp#page-object-design-pattern

Features
--------

- The view `@@inspector` now also displays the interfaces of its context.

Fixes
-----

- Fix styling issue in forms having lists with multiple entries (e. g. possible
  values of choice field on user defined field of entity).

Other changes
-------------

- Bring test coverage to 100 % including tests themselves but without webdriver
  tests.


Previous Versions
=================

See `OLD_CHANGES.rst`_.

.. _`OLD_CHANGES.rst` : https://bitbucket.org/icemac/icemac.addressbook/src/tip/OLD_CHANGES.rst

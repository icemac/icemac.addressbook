==========
Change log
==========


4.1 (unreleased)
================

- Update to a version of `icemac.recurrence` which fixed a bug in the
  computation of monthly recurring events on DST borders.


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


3.0 (2017-02-04)
================

Backward incompatible changes
-----------------------------

- Update to `py.test >= 2.8`. This version no longer allows a fixture to depend
  on an equally named fixture in another package. This requires a restructuring
  of the fixtures: Packages depending on `icemac.addressbook` can no longer
  e. g. depend the `zcmlS` fixture but have to provide there own full blown
  ZCML fixture. The fixtures which can be reused where moved to
  ``icemac.addressbook.fixtures``. ``icemac.addressbook.conftest`` should no
  longer be used or imported from foreign packages as this leads to problems
  with the new py.test version. The reusable helper functions have been moved
  to ``icemac.addressbook.testing``.


Other
-----

- Update most libraries needed for the address book to their newest versions.


2.10 (2017-01-20)
=================

Features
--------

- Add a search result handler which renders a list of the selected persons with
  a check-box in front.

- Style text input fields better.

- Style the print output properly.

Other
-----

- Update most libraries needed for the address book to their newest versions.

- Pack the ZODB during update to a newer address book version.


Previous Versions
=================

See `OLD_CHANGES.rst`_.

.. _`OLD_CHANGES.rst` : https://bitbucket.org/icemac/icemac.addressbook/src/tip/OLD_CHANGES.rst

==========
 Download
==========

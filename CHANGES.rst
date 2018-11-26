==========
Change log
==========

8.1 (unreleased)
================


Other changes
-------------

- Add some `operations tips <https://icemacaddressbook.readthedocs.io/en/latest/operations.html>`_ for the address book.

- Update most libraries needed for the address book to their newest versions.


8.0 (2018-10-13)
================

Backwards incompatible changes
------------------------------

- No longer install test and debugging infrastructure in a production
  environment by default.

- Rename `Apply` button to `Save`.

- Add ZEO server running the database. This requires a different commands to
  start and stop the address book and the database server, see
  `documentation <https://icemacaddressbook.readthedocs.io/en/latest/runtheapplication.html>`_.

- Remove scripts which drop into a debugger on an exception and their
  infrastructure (`bin/debug_ajax` and `bin/debug_pdb`).

Other changes
-------------

- Update most libraries needed for the address book to their newest versions.


7.0.4 (2018-08-05)
==================

- No longer show an empty read more URL in the cookie consent banner if no
  data protection URL is set.

- Fix styling issues introduced in version 7.0.


7.0.3 (2018-08-04)
==================

- Fix contents of created `buildout.cfg`.


7.0.2 (2018-08-04)
==================

- Fix installation code to work with ``icemac.install.addressbook >= 1.3.1``.


7.0.1 (2018-08-04)
==================

- No longer use `bootstrap.py` of ``zc.buildout`` during installation as
  it can produce endless loops. Expect `bin/buildout` to be already installed
  via ``virtualenv``.


7.0 (2018-08-03)
================

Backward incompatible changes
-----------------------------

- Move function ``.testing.assert_forbidden()`` as a method to
  ``.testing.Browser.assert_forbidden()`` and expect that the user is already
  logged-in thus no longer requiring ``username`` as argument.

- Drop ``.testing.SiteMenu.assert_correct_menu_item_is_tested()``. Use
  ``.testing.SiteMenu.get_menu_item_title_under_test()`` instead and compare
  its result with `menu_item_title`.

- Change license from ZPL to MIT.

Features
--------

- Add ability to configure the following links during setup. They are shown at
  the bottom of each page:

  + imprint
  + data protection declaration

- Add a `schema_name` index to distinguish between entities in the catalog.

- Add an ability to disable `handle_errors` to debug all exception types.
  See https://icemacaddressbook.readthedocs.io/en/latest/hacking.html

- Add cookie usage consent dialog.

- Add ability to run tests in parallel.


User interface
--------------

- No longer render the form submit buttons on the bottom border of the screen.
  This did not work very well on mobile devices.


Other
-----

- Update most libraries needed for the address book to their newest versions.

- Drop dependency on `gocept.selenium` by writing pure `selenium` tests. This
  requires ``geckodriver`` to run the tests. (See documentation about
  `running the tests`_.)

.. _`running the tests` : https://icemacaddressbook.readthedocs.io/en/latest/runthetests.html#prerequisites-for-the-browser-tests


6.0.2 (2018-03-17)
==================

- Fix update process to be again able to copy data from the old installation.
  This got broken in 6.0.


6.0.1 (2018-03-17)
==================

- No longer build `lxml` via buildout recipe, as it might break and the
  installation procedure of `lxml` should now be stable enough.


6.0 (2018-03-16)
================

Backward incompatible changes
-----------------------------

- Add a `schema_name` index to distinguish between entities in the catalog.

Bug fixes
---------

- Fix the breadcrumbs on the about page and the logout page.

- Searching for `*` in name search no longer provokes an error.

Other
-----

- Move the documentation from
  https://bitbucket.org/icemac/icemac.addressbook/wiki/ to
  https://icemacaddressbook.readthedocs.io

- Deprecate the `Manual package installation`_ variant to install this
  package. It will be no longer supported in the next major version.
  Switch to `Guided package installation`_ now as described in
  `Upgrade installation`_.

- Update most libraries needed for the address book to their newest versions.

.. _`Manual package installation` : https://icemacaddressbook.readthedocs.io/en/latest/manualinstallation.html
.. _`Guided package installation` : https://icemacaddressbook.readthedocs.io/en/latest/guidedinstallation.html
.. _`Upgrade installation` : https://icemacaddressbook.readthedocs.io/en/latest/upgrade-installation-manual-to-guided.html


Previous Versions
=================

See `OLD_CHANGES.rst`_.

.. _`OLD_CHANGES.rst` : https://bitbucket.org/icemac/icemac.addressbook/src/default/OLD_CHANGES.rst

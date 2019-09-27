==========
Change log
==========

9.0 (2019-09-27)
================

Backwards incompatible changes
------------------------------

- Drop support for `Manual package installation` which was deprecated since
  version 6.0. If you are still using it, switch to
  `Guided package installation` as described in `Upgrade installation`_.

- Integrate `src/icemac/addressbook/base.zcml` into
  `src/icemac/addressbook/roles.zcml`.

Features
--------

- Add a search result handler which renders a birthday list.

- Add a cron job which does a daily backup of the database.

- Add an archive and the ability to archive persons.

  - The archive can only be accessed by one of the two new roles:

    + archive visitor -- read only access in the archive
    + archivist -- access to the archive plus ability to un-archive persons

  - Archived persons cannot be found using the search abilities of the
    address book.

  - Add a search result handler which can move persons to the archive.

  - To disable the archive feature see the `archive documentation`_.

- Allow to edit the labels and descriptions of pre-defined fields.

- Document how to uninstall the address book.

- Add ability to deselect tabs in the main menu.

- Users without any roles no longer get HTTP-403 Forbidden but can access a
  minimal part of the application.

Changes in testing
------------------

- Switch Selenium tests from Firefox to Chrome by default requiring
  `chromedriver`, but allow to keep using Firefox via an environment variable.
  Details see `documentation`_.

- Drop support for profiling using `z3c.profiler`.

Other changes
-------------

- Add some `operations tips <https://icemacaddressbook.readthedocs.io/en/latest/operations.html>`_ for the address book.

- Update most libraries needed for the address book to their newest versions.

- Store messages rendered in UI in RAM instead of in ZODB.

- Render URLs of the source code and documentation on the PyPI page.

- Drop reruns of tests.

- Show test failures instantly.

Bug fixes
=========

- First time installation no longer asks for migration.

- During installation no longer store the admin password in the config file and
  no longer present the password in clear text during update installation.


8.0 (2018-10-13)
================

Backwards incompatible changes
------------------------------

- No longer install test and debugging infrastructure in a production
  environment by default.

- Rename `Apply` button to `Save`.

- Add ZEO server running the database. This requires a different commands to
  start and stop the address book and the database server, see
  `documentation`_.

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


Previous Versions
=================

See `OLD_CHANGES.rst`_.

.. _`OLD_CHANGES.rst` : https://bitbucket.org/icemac/icemac.addressbook/src/default/OLD_CHANGES.rst
.. _`documentation` :  https://icemacaddressbook.readthedocs.io/en/latest/runtheapplication.html
.. _`Upgrade installation` : https://icemacaddressbook.readthedocs.io/en/latest/upgrade-installation-manual-to-guided.html
.. _`archive documentation` :  https://icemacaddressbook.readthedocs.io/en/latest/operations.html

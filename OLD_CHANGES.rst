=============
 Old changes
=============

Change log of releases more than 2 minor or even major versions behind current
version.


9.0.1 (2019-10-04)
==================

- Update to a trollius version which is still on PyPI.


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


1.9.0 (2012-12-29)
==================

Features
--------

- Added search result handler which prints the names of the selected persons
  als comma separated list.


Bugfixes
--------

- Login in a virtual hosting environment might have led to not accessible
  URLs. This was fixed by using the whole URL in the `camefrom` parameter.

Other
-----

- Updated to `Zope Toolkit 1.1.4`_ for dependent packages.

- Updated other dependent packages (outside ZTK) to newest versions.

- Moved `chameleon-cache` into `var` directory.

.. _`Zope Toolkit 1.1.4`: http://docs.zope.org/zopetoolkit/releases/overview-1.1.4.html


1.8.1 (2012-04-20)
==================

Features
--------

- Added favicon.ico to the application.

- Split preferences into multiple groups.

Bugfixes
--------

- The search result handler which updates data did not update the catalog,
  so these changes were invisible for the search. Updated catalog and search
  result handler.

- User preferences were stored globally instead of locally in the address
  book of the user. Users with the same internal ID shared preferences
  across address books. As the internal IDs are simply a counter this
  happened every time if using the multi-client capability.

  The problem was fixed by storing user preferences locally and copying
  existing global preferences over to the each address book where a user for
  the internal user ID of the preferences exists.

Other
-----

- Updated other dependent packages (outside ZTK) to newest versions.

- Using Fanstatic – a WSGI middleware – to deliver CSS and JS instead of
  ``hurry.resource``.


1.8.0 (2011-12-14)
==================

Features
--------

- Added search result handler which allows to send an e-mail to the persons
  found by the search.

Bugfixes
--------

- The search result handler which updates data did not handle keywords well,
  it was not possible to remove a keyword from a person using that handler.


Other
-----

- Added some Screenshots_ to the SourceForge_ page.

- Using `Chameleon 2` as HTML render engine resulting in faster page
  rendering. (Test run in half of the time now.)

- Updated to `Zope Toolkit 1.1.3`_ for dependent packages.

- Updated other dependent packages (outside ZTK) to newest versions.

- Dropped some package dependencies which only existed for compatibility
  reasons with older versions. Data gets converted during first start-up.

.. _`Zope Toolkit 1.1.3`: http://docs.zope.org/zopetoolkit/releases/overview-1.1.3.html

1.7.0 (2011-11-03)
==================

General
-------

- Dropped support for Python 2.5, so currently only Python 2.6 is supported.


UI changes
----------

- Previously search results could only be exported. The options have been
  widened, so different handlings of search results are possible. So
  deletion of the selected persons has been moved to these search result
  handlers.

- Added explanation text to search from.

Features
--------

- Added a new search type: Search for person names. You may use wildcards in
  this search (? for a single character or * for multiple characters).

- Search results now display the columns the user selected in his personal
  preferences.

- Added search result handler to modify a single field on all selected persons
  in the search result. Depending on the kind of the field different operations
  are possible (replace with, append to, remove from, add to, multipy with,
  intersect with, ...). Only users with "Administrator" role can use this
  handler as wrong usage might be dangerous for the data.


Bug fixes
---------

- Running the address book in a vhost environment did not allow to access the
  about screen, as it was only registered for the root folder.

Other
-----

- Updated to `Zope Toolkit 1.1`_ for dependent packages.

- Integrated `decorator` package into distribution as needed version is
  prone to disappear from PyPI.

- Changed test setup to use `plone.testing` layer.

.. _`Zope Toolkit 1.1`: http://docs.zope.org/zopetoolkit/releases/overview-1.1.html


1.6.0 (2011-02-03)
==================

Features
--------

- Added ability to sort the fields of the entities.

Bug fixes
---------

- It is no longer possible to add new fields to the 'main adresses and
  numbers' entity as it makes no sense and breaks the address book.


1.5.0 (2010-11-23)
==================

Features
--------

- Added support for Python 2.6.

- Added an "about addressbook" view which shows the version number. The blue
  "i" right of "icemac.addressbook" in each view is a link to it.

- Added messages telling about successful actions, e. g. applying or
  canceling a form.

- Made it possible to sort the entities.

- Made 'main adresses and numbers' an entity, so it could be sorted along
  with the other entities.

- Added ability to delete the persons found in a search. User must have the
  administrator role to use this feature as it might be dangerous.

- Added installation option to configure that the address book process sould
  run as another user than the one who started it.

Bug fixes
---------

- When copying a person, the creation dates and modification dates of the
  addresses in the copied person are changed along the person.


Other changes
-------------

- Updated to `Zope Toolkit 1.0`_ for dependent packages.

.. _`Zope Toolkit 1.0`: http://docs.zope.org/zopetoolkit/releases/overview-1.0.html


1.4.0 (2010-08-19)
==================

Features
--------

- Added user preferences to customize the columns displayed in person list.

- Added batching to person list (customizable in the user preferences).

- Each table shows its rows in alternating colors.


Other changes
-------------

- Using `Zope Toolkit 1.0a2`_ instead of managing our own versions of
  dependent packages.

.. _`Zope Toolkit 1.0a2`: http://docs.zope.org/zopetoolkit/releases/overview-1.0a2.html


1.3.0 (2010-03-20)
==================

- Feature: Replaced `Simple single keyword search` by `Keyword search` which
  allows to search for multiple keywords concatenated by `and` or `or`.


1.2.0 (2010-02-06)
==================

- Feature: Added ability to clone a person.

1.1.2 (2010-01-27)
==================

- Search result table displayed only 50 entries. Now it displays all
  search results ordered by name.


1.1.1 (2010-01-25)
==================

- Fixed version of `icemac.ab.locales`.


1.1.0 (2010-01-25)
==================

Features
--------

- Added translation to XLS export files.

- Added creator, last modifier and modification date metadata to
  objects.

Bugfixes
--------

- When two users are exporting at the same time this could end in
  broken export files.

- On the person edit form:

  - the the last modification dates of the entries (postal address,
    phone number etc.) where the one of the person.

  - the keywords field was not correctly implemented: it was always
    marked as changed so the a new last modification date on the
    person was set, even when nothing has been changed.

  - editing a field of an entry did not change the modification date
    of this entry but of the person.

1.0.1 (2010-01-13)
==================

- Bugfix: The value fields of a user defined field of type `choice`
  could not contain non ascii characters. This broke the usage of the
  field on any object.


1.0.0 (2009-12-29)
==================

- Translated UI into German.

- Displaying modification date of adresses now.

- Dropped some package dependencies which existed for compatibility
  reasons with older versions. To upgrade to this version you might
  need to upgrade to 0.5.4 first. (See Update_.)


0.5.4 (2009-12-20)
==================

- Users which are defined inside an address book having the
  `Administrator` role, were not able to edit address book entities.


0.5.3 (2009-11-22)
==================

- After the last fix `delete all persons` did not delete any
  persons. This is now fixed.


0.5.2 (2009-11-21)
==================

- `Delete all persons` no longer tries to delete the persons which are
  users. Previously this function broke when there were users defined
  in the address book.

- Moved the function to delete a whole address book to the overview
  page of all address books, as users defined inside an address book
  are not allowed to delete their address book.


0.5.1 (2009-11-21)
==================

- Fixed namespace package declaration so the package can be installed
  on a plain vanilla python (even without setuptools installed).


0.5 (2009-11-21)
================

Features
--------

- Users having the role `Administrator` can delete all persons in the
  address book or even the whole address book on the address book edit
  form.

- Last modification time of objects is now stored and displayed (in
  UTC!).

- Users having the role `Administrator` can import data in the master
  data area.

- Added ability to enter additional packages names at installation
  (e. g. to install a specific import file readers).

- Users having the role `Administrator` can add new fields to address
  book entities in the master data area. These fields as useable for
  editors and visitors, too.

Removed features
----------------

- Removed some fields which are not always necessary and which can be
  re-added when needed as user defined fields:

  - state field on the postal address (only displayed German
    states, though),

  - sex field on person,

  - notes fields on address book, postal address, phone number, e-mail
    address, home page address, file and keyword,

  - kind fields on postal address, phone number, e-mail address and
    home page address.


Bug fixes
---------

- Uploading a new file changes the stored name of the file.

- When uploading a file with an unknown mime type (aka
  `application/octet-stream`) the actual mime type is guessed using
  the file extension and file content.

- The person list is now ordered by the displayed titles instead of
  the internal ids.


0.4 (2009-05-15)
================

Features
--------

- Files can be uploaded and added to persons. (Files are stored as
  ZODB-Blob-Objects.)

- Added logging of page accesses to `access.log`.

- ``install.py`` now asks for hostname and portnumber and logging
  configuration, so changing ``deploy.ini`` is no longer necessary.


0.3.3 (2009-04-05)
==================

- Added two package dependencies which are necessary to convert an
  existing ZODB of a previous address book version.


0.3.2 (2009-04-03)
==================

- Fixed the sort order of the links in the master data section.


0.3.1 (2009-03-31)
==================

- Fixed wrong recipe version.


0.3 (2009-03-31)
================

Features
--------

- Added user management. There is now only one administrative user
  created during installation. This user can log-in using basic
  auth. He can create new users from existing persons inside the
  address books (See `Master data --> Users`.)


Bug fixes
---------

- Made the AddressBook skin the default skin.


Other changes
-------------

- Dropped support for Python 2.4.

- Renamed role `icemac.addressbook.administrator` to
  `icemac.addressbook.global.administrator` so all global roles have
  the same naming scheme.

- Removed ZMI (Zope Management Interface) from skins in production
  environment. There is a buildout config in ``profiles/zmi.cfg``
  which enables ZMI.


0.2 (2009-01-02)
================

Features
--------

- Multiple postal addresses, e-mail addresses, phone numbers and home
  page addresses per person are now possible.

- Added XLS export for all stored data (not only the default
  addresses).

- Added new attribute `kind` to postal address. Split `street` into
  `address prefix` and `street`.

- Overview page of all address books now shows number of entries in
  each address book.

Bug fixes
---------

- E-Mail adresses with hyphen in host name where not enterable due to
  a picky constraint.

- After changing a keyword title, persons using this keyword where no
  longer found in the keyword search because the index was not
  updated.

- Changed sort order on person edit form: phone number is now
  displayed before e-mail address. Changed XLS export accordingly.

0.1.2 (2008-11-23)
==================

- Added recipe to safely install lxml dependency.


0.1.1 (2008-11-10)
==================

- Initial public release.


0.1 (2008-11-08)
================

- Created PyPI homepage.

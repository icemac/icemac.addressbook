=============
 Old changes
=============

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

==========
Change log
==========

1.10.0 (unreleased)
===================

Features
--------

- Added welcome page displayed after login. So additional packages might
  provide roles which do not allow to access the persons in the address
  book.

- Added ability to user preferences to set current time zone. Datetimes,
  e. g. creation date, modification date and user defined fields of type
  datetime, are converted to the selected time zone. Default is UTC.

- Added JavaScript calendar widget to datetime fields.

- Added number of displayed persons in search result handler which displays
  the names of the selected persons (new in 1.9.0).

- Now displays the name of the address book in HTML title tag and as
  headline inside the application.

- Moved link to edit form of address book from tabs to master data.

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


Previous Versions
=================

See ``OLD_CHANGES.txt`` inside the package.

==========
 Download
==========


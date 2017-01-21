==========
Change log
==========


2.11 (unreleased)
=================

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


Previous Versions
=================

See `OLD_CHANGES.rst`_.

.. _`OLD_CHANGES.rst` : https://bitbucket.org/icemac/icemac.addressbook/src/tip/OLD_CHANGES.rst

==========
 Download
==========

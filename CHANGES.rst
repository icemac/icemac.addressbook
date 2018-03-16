==========
Change log
==========


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


Previous Versions
=================

See `OLD_CHANGES.rst`_.

.. _`OLD_CHANGES.rst` : https://bitbucket.org/icemac/icemac.addressbook/src/tip/OLD_CHANGES.rst

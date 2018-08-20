.. _runthetests:

Run the tests
=============

Running the tests is independent from your chosen installation kind but the prerequisites differ.

Run the unit tests
------------------

Prerequisites for the unit tests
++++++++++++++++++++++++++++++++

If you have used the :ref:`package-installation` method you have to install the test scripts first::

  $ cd current
  $ ../bin/buildout install node pytest


Run the unit tests
------------------

Run the unit tests using::

  $ bin/py.test -k "not webdriver"

Run all tests
-------------

These tests include some tests which require an actual browser to run.

Prerequisites for the browser tests
+++++++++++++++++++++++++++++++++++

These prerequisites are only needed to run some tests in an actual browser:

* `geckodriver`_ matching the ``selenium`` version used in the address book,
  see `profiles/version.cfg`_ resp. the file you are actually using. It has to
  be installed in the search path.

* Firefox (version as described by `geckodriver`_)

Run all tests
+++++++++++++

Run all tests including the browser tests using::

   $ bin/py.test

.. _geckodriver : https://github.com/mozilla/geckodriver/releases
.. _`profiles/version.cfg` : https://bitbucket.org/icemac/icemac.addressbook/src/default/profiles/versions.cfg

.. _runthetests:

Run the tests
=============

Running the tests is independent from your chosen installation kind but the prerequisites differ.

Unit tests
----------

Prerequisites
+++++++++++++

If you have used the :ref:`package-installation` method you have to install the test scripts first::

  $ cd current
  $ ../bin/buildout install node pytest


Run the unit tests
++++++++++++++++++

Run the unit tests using::

  $ bin/py.test -k "not webdriver"

All tests
---------

These tests include some tests which require an actual browser to run.

Prerequisites for the browser tests
+++++++++++++++++++++++++++++++++++

These prerequisites are only needed to run some tests in an actual browser:

* Fairly recent `chromedriver`_ version. It has to be installed in the search
  path.

* Google Chrome (a version matching your `chromedriver`_ version)

Run all tests
+++++++++++++

Run all tests including the browser tests using::

   $ bin/py.test

To additionally show the actual browser during the tests, call them using::

   $ NOT_HEADLESS=1 bin/py.test

.. _chromedriver : http://chromedriver.chromium.org/downloads
.. _`profiles/version.cfg` : https://bitbucket.org/icemac/icemac.addressbook/src/default/profiles/versions.cfg

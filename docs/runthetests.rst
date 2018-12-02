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

These prerequisites are only needed to run some tests in an actual browser.

Default prerequisites
.....................

* Fairly recent `chromedriver`_ version. It has to be installed in the search
  path.

* Google Chrome (a version matching your `chromedriver`_ version)

Alternative prerequisites
.........................

* `geckodriver`_ matching the ``selenium`` version used in the address book,
  see `profiles/version.cfg`_ resp. the file you are actually using. It has to
  be installed in the search path.

* Firefox (version as described by `geckodriver`_)

Run all tests
+++++++++++++

Run all tests including the browser tests using::

    $ bin/py.test

*Caution:* By default the browser does not show up, it runs in headless mode.
To additionally show the actual browser during the tests, call them using::

    $ NOT_HEADLESS=1 bin/py.test


To run the tests in Firefox, call them using::

    $ SELENIUM_FIREFOX=1 bin/py.test

Firefox also supports the non-headless mode::

    $ SELENIUM_FIREFOX=1 NOT_HEADLESS=1 bin/py.test

.. _chromedriver : http://chromedriver.chromium.org/downloads
.. _geckodriver : https://github.com/mozilla/geckodriver/releases
.. _`profiles/version.cfg` : https://bitbucket.org/icemac/icemac.addressbook/src/default/profiles/versions.cfg

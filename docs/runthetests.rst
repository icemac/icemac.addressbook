.. _runthetests:

Run the tests
=============

Running the tests is independent from your chosen installation kind.


Run the unit tests
------------------

Run the unit tests using::

  $ bin/py.test -k "not webdriver"

Run all tests
-------------

These tests include some tests which require an actual browser to run.

Prereqisites for the browser tests
----------------------------------

These prereqisites are only needed to run some tests in an actual browser:

* Selenium Server from SeleniumHQ_

* Firefox (version number >= 21.0 but < 46.0)

Run all tests
-------------

To run all tests including the browser tests following these steps:

1. set the variable ``GOCEPT_WEBDRIVER_FF_BINARY`` like this::

   $ export GOCEPT_WEBDRIVER_FF_BINARY='<Path to the Firefox binary>'

2. start the Selenium server::

   $ java -jar <Path to Selenium-Server-jar>

3. run all tests using::

   $ bin/py.test

.. _SeleniumHQ: http://seleniumhq.org/download/

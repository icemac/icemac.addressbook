==============
 Installation
==============

Prerequisites
=============

* You only need Python 2.6.x. (Other Python versions are currently
  not supported.)

There are two variants for installation:

  * Package installation (to be preferred)

  * Source installation (for development)

Package installation
====================

Follow these steps if you want to install the pre-packaged address book
(preferred way):

First installation
------------------

CAUTION: icemac.addressbook can't be installed using ``easy_install`` or
``pip``, you have to follow these simple steps.

Neither you need any root privileges nor it installs anything outside
its directory.

1. Download the source distribution (see Download_).

2. Extract the downloaded file.

3. Run ``install.py`` using your desired python, e. g.::

   $ python2.6 install.py

4. Answer the questions about admin user name, password and so on.

5. Run the tests. See `Run the tests`_

6. Start the application. See `Run the application`_

Update
------

- If you are updating from version 0.3.x or earlier follow the steps
  described in `First installation`_ followed by the steps described
  in `Second part of steps for really old versions`_.

- If you are updating from version 0.4 or newer follow these steps:

   1. Download and extract the source distribution (see Download_) to a
   new a directory.

   2. Run ``install.py`` using your desired python added by the path
   to the previous installation. This way values you entered
   previously are used as defaults instead of the application
   defaults.  Example::

     $ python2.6 install.py ../icemac.addressbook-0.4

   3. Answer the questions about admin user name, password and so on.

   4. Start the new instance of the application.

- If you get an error when running the application after updating
  which looks like::

    zope.generations.interfaces.UnableToEvolve: (..., u'icemac.addressbook', ...)

  - If you upgrade from version 0.x then you have to upgrade to version 0.5.4
    first and start the application, so that legacy data can be
    converted. Version 1.x is no longer compatible with these older versions.

  - You might need to **not** install any additional packages during these
    upgrade steps as the installer always tries to install the newest
    versions of the additonal packages which might not be compatible with
    the older versions.


Second part of steps for really old versions
--------------------------------------------

1. Stop the old instance of the application.

2. Create a backup of the ZODB og the old instance using::

   $ bin/backup

3. Copy the backup directory (``var/backups``) to the new instance.

4. Restore the backup into the new instance using::

   $ bin/restore

5. Start the new instance of the application.


Source installation
===================

1. Get the source code::

   $ hg clone https://bitbucket.org/icemac/icemac.addressbook

2. Install the sources::

   $ cd icemac.addressbook
   $ printf "[buildout]\nextends = profiles/%s\n" dev.cfg > buildout.cfg
   $ python2.6 bootstrap.py
   $ bin/buildout


Run the tests
=============

Running the tests is independent from your choosen installation kind.

Run the unit tests and functional tests using::

  $ bin/test

To run the Selenium tests you additionally need: a running Selenium Server.
Download "Selenium Server" from SeleniumHQ_.  Start it like any other
``jar`` package is started on your operating system. Run all tests using::

  $ bin/test --all

.. _SeleniumHQ: http://seleniumhq.org/download/

Run the application
===================

Running the application is independent from your choosen installation kind.

To run the application instance in foreground start using::

  $ bin/addressbook fg

To run it as a demon process start using::

  $ bin/addressbook start

To stop the demon process call::

  $ bin/addressbook stop

The default URL is to access the application is::

  http://127.0.0.1:8080

To log-in at this URL you need a username and password.

 * If you installed via package installation you had to chose them when
   running ``install.py``. They are stored in ``admin.zcml``.

 * If you installed the sources you find username and password in
   ``dev_admin_user.zcml``.

Create a new address book using the `add address book` link on the
right. How to create new users inside this address book is described
in `Create new users`_.


Change configuration of the installation
========================================

This section is only valid if you chose package installation.

The values you entered during installation resp. update are stored in
a file named `install.user.ini` in the address book directory.

To change the configuration values call `install.py` using python and
enter a `.` as parameter like this::

  $ python2.6 install.py .

The configuration questions get presented to you with your previously
entered values as default.

To remove additional packages you have to edit the ``[package]``
section of `install.user.ini`. There is currently no other way for
removal.

To remove the user name which should own the process you have to edit the
``[server]`` section of `install.user.ini`. Remove the value from the
``user`` line.

=================
 User management
=================

Roles
=====

Access to the address book is only granted after authentication. There
are three roles to authorize a user:

- visitor: visit all person's data, search and export, change own
  password

- editor: permissions of visitor + edit all person's data, change own
  log-in name

- administrator: permissions of editor + create and change address
  book and users

Create new users
================

Users are persons from the address book augmented by log-in
information.

To create the first new user inside an address book the adminstrator
(who was created in `First installation`_) has to log-in and then do
the following:

  1. create a new person with an e-mail address using `Add person`.

  2. create a new user using `Master data --> Users --> Add user`.

The newly created user has now a log-in (e-mail address) for the
address book the person belonges to.
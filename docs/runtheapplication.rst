.. _runtheapplication:

===================
Run the application
===================

Running the application is independent from your chosen installation method.

To run the application instance in the foreground start it using::

  $ bin/addressbook fg

To run it as a demon process start it using::

  $ bin/addressbook start

To stop the demon process call::

  $ bin/addressbook stop

The default URL to access the application is:

  http://127.0.0.1:8080

(You may have changed the port number during the :ref:`installation`\ .)

To log-in at this URL you need a user name and a password.

* If you installed via :ref:`package-installation` you had to chose both during
  the installation. They are stored in ``admin.zcml``.

* If you installed via :ref:`source-installation` you find user name and
  password in ``dev_admin_user.zcml``.

Create a new address book using the `add address book` link on the
right. How to create new users inside this address book is described
in :any:`usermanagement`.

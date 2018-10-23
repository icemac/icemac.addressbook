.. _loginintotheapplication:

===========================
Log-in into the application
===========================

The default URL to access the application is:

  http://127.0.0.1:8080

(You may have changed the port number during the :ref:`installation`\ .)

.. caution:: This URL is only accessible for a browser running on the same
             machine as the application. If you are installing it on an
             (external) server you might need to create a port forward to your
             local machine.

To log-in at this URL you need a user name and a password.

* If you installed via :ref:`package-installation` you had to chose both during
  the installation. They are stored in ``admin.zcml``.

* If you installed via :ref:`source-installation` you find user name and
  password in ``dev_admin_user.zcml``.

Create a new address book using the `add address book` link on the
right. How to create new users inside this address book is described
in :any:`usermanagement`.

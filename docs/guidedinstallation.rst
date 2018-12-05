.. _package-installation:

===========================
Guided package installation
===========================

Follow these steps if you want to install the pre-packaged address book from
PyPI. (This is the preferred way of the installation.)

.. note::

    ``icemac.addressbook`` can't be installed directly using
    ``easy_install`` or ``pip``, you have to follow these simple steps.

Neither you need any root privileges nor it installs anything outside its
directory.

Installation steps:

#. Create a `virtualenv` using::

   $ virtualenv-2.7 addressbook

#. Change into the directory of the `virtualenv` using::

   $ cd addressbook

#. Install the installation script using::

   $ bin/pip install icemac.install.addressbook

#. Start the installation

   *  call::

      $ bin/install-addressbook VERSION_NUMBER

   * ``VERSION_NUMBER`` can be omitted to install the latest version or
     should be replaced by the desired version.

#. Answer the questions about admin user name, password and so on.

#. Change into the installation directory using::

   $ cd current

#. :ref:`runthetests`

#. :ref:`runtheapplication`

#. :ref:`loginintotheapplication`

#. :ref:`operations`

.. include:: cronjobs.rst

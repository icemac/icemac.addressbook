==================================
Update guided package installation
==================================

This steps can be applied if you installed via :ref:`package-installation`.

#. Switch to the directory you created for the address book, in :ref:`package-installation` it was suggested to call it ``addressbook``::

    $ cd addressbook

#. Update the installer package using::

    $ bin/pip install -U icemac.install.addressbook

#. Start the update

   * using::

      $ bin/install-addressbook VERSION_NUMBER

   * ``VERSION_NUMBER`` can be omitted to install the latest version.

#. Answer the questions about admin user name, password and so on, they should
   be pre-filled with the values of the previous installation.

   If the upgrade procedure breaks with an error, first try to upgrade to the
   next major version (first digit of the version number) which comes after
   your current version.

#. Start the new instance of the application as described in
   :ref:`runtheapplication`.

#. You might archive the previous version

   * by calling::

      $ bin/archive-addressbook VERSION_NUMBER

   * Where ``VERSION_NUMBER`` is the version number of the previous version.

   * It creates an archive of the installation folder and removes the
     installation folder afterwards.

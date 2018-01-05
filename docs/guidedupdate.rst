==================================
Update guided package installation
==================================

This steps can be applied if you installed via :ref:`package-installation`.

1. Update the installer package using::

    $ bin/pip install -U icemac.install.addressbook

2. Start the update

   * using::

      $ bin/install-addressbook VERSION_NUMBER

   * ``VERSION_NUMBER`` can be omitted to install the latest version.

3. Answer the questions about admin user name, password and so on, they should
   be pre-filled with the values of the previous installation.

4. Start the new instance of the application as described in
   :ref:`runtheapplication`.

5. You might archive the previous version

   * by calling::

      $ bin/archive-addressbook VERSION_NUMBER

   * Where ``VERSION_NUMBER`` is the version number of the previous version.

   * It creates an archive of the installation folder and removes the
     installation folder afterwards.

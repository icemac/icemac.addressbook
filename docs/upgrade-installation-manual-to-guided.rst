.. _upgrade-to-guided-installation:

===============================================================
Upgrade installation from manual to guided installation variant
===============================================================

The following steps are necessary to upgrade an installation made with the
deprecated manual installation method to the recent
:ref:`package-installation` method.


#. Install `virtualenv`, see :any:`prerequisites`.

#. Make a new installation as described in :ref:`package-installation`.
   Including the creation of a new `virtualenv`. The answers to the questions
   about user name etc. do not matter. But using the same eggs directory speeds
   up the process. Do not try to migrate the old address book content to the
   new instance, yet.

#. Change into the installation directory using::

   $ cd current

#. Remove the `buildout.cfg` created by the installation process::

   $ rm buildout.cfg

#. To run the migration

   * call::

     $ ../bin/python2.7 install.py PATH_TO_PREVIOUS_ADDRESSBOOK_INSTALLATION

   * ``PATH_TO_PREVIOUS_ADDRESSBOOK_INSTALLATION`` has to be replaced with the
     path to the installation directory of the address book (the one created
     when extracting the source distribution).

   * The questions during the installation should be pre-filled with the values
     from your previous installation.

   * Make sure to allow to migrate the old address book content to the new
     instance when asked during the installation process.

#. :ref:`runthetests`

#. :ref:`runtheapplication`

#. If the installation was successful you can remove the old installation.

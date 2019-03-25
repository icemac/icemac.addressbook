========================================
Change configuration of the installation
========================================

This description can only be applied if you chose the
:ref:`package-installation` method.

The values you entered during installation resp. update are stored in
a file named ``install.user.ini`` in the ``current`` installation directory
of the address book.

You can change the configuration values like this:

#. Switch to the directory you created for the address book, in
   :ref:`package-installation` it was suggested to call it ``addressbook``::

       $ cd addressbook

#. If you have made changes to the file ``buildout.cfg`` move it aside to be
   able to port the changes over afterwards. Otherwise just remove the file.

#. Call the script to change the configuration::

   $ bin/change-addressbook-config

#. The configuration questions get re-presented to you with your previously
   entered values as defaults.

#. The address book instance has to be restarted which is done by the script
   if you want this. Otherwise see :ref:`runtheapplication`.

.. caution::

    To remove additional packages you have to edit the ``[package]``
    section of ``install.user.ini``. There is currently no other way for
    removal. But be careful this might break your address books in the browser
    if the removed package(s) already stored data in the database.
    Afterwards call ``bin/change-addressbook-config`` as described above.

.. caution::

    To remove the user name which should own the process you have to edit the
    ``[server]`` section of ``install.user.ini``. Remove the value from the
    ``user`` line.
    Afterwards call ``bin/change-addressbook-config`` as described above.

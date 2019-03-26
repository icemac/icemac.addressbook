=========
Uninstall
=========

If you want to uninstall the address book consider the following steps:

#. Switch to the directory you created for the address book, in
   :ref:`package-installation` it was suggested to call it ``addressbook``::

      $ cd addressbook

#. Stop the address book using::

   $ bin/svctl stop all
   $ bin/svctl shutdown

#. Remove the created cronjobs via::

   $ crontab -e

#. Delete the whole installation directory.

#. Maybe remove the configuration made for the address book from your frontend
   server (Apache, ngnix, …).

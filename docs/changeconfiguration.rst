========================================
Change configuration of the installation
========================================

This description can only be applied if you chose the
:ref:`package-installation` method..

The values you entered during installation resp. update are stored in
a file named ``install.user.ini`` in the address book's directory.

To change the configuration values call ``install.py`` and use ``.`` as parameter like this::

  $ ../bin/python2.7 install.py .

The configuration questions get re-presented to you with your previously entered values as default.

To remove additional packages you have to edit the ``[package]``
section of ``install.user.ini``. There is currently no other way for removal.
But be careful this might break your address books in the browser if the
removed package(s) already stored data in the database.

To remove the user name which should own the process you have to edit the
``[server]`` section of ``install.user.ini``. Remove the value from the ``user`` line.

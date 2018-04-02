=======
Hacking
=======

Fork me on: https://bitbucket.org/icemac/icemac.addressbook

File an issue on: https://bitbucket.org/icemac/icemac.addressbook/issues

Create the documentation using ``tox``.

See :ref:`source-installation`, too.

Debug the application
=====================

If you disable `handle_errors` you get a full traceback for each exception type
rendered on your console. To do so start the address book using::

    $ HANDLE_ERRORS=0 bin/addressbook fg

.. caution:: This should not be used in a production environment!


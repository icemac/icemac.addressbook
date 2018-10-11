.. _source-installation:

===================
Source installation
===================

This installation should only be used to work on the address book code itself.

1. Get the source code::

   $ hg clone https://bitbucket.org/icemac/icemac.addressbook

2. Install the sources::

   $ cd icemac.addressbook
   $ virtualenv-2.7 .
   $ bin/pip install zc.buildout
   $ printf "[buildout]\nextends = profiles/%s\n" dev.cfg > buildout.cfg
   $ bin/buildout

3. :ref:`runthetests`

4. To run the application you have to start the database
   (in demon mode) and the actual application in the foreground::

   $ bin/zeoserver start
   $ bin/addressbook

5. :ref:`loginintotheapplication`

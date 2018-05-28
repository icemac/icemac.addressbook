.. _source-installation:

===================
Source installation
===================

This installation should only be used to work on the address book code itself.

1. Get the source code::

   $ hg clone https://bitbucket.org/icemac/icemac.addressbook

2. Install the sources::

   $ cd icemac.addressbook
   $ printf "[buildout]\nextends = profiles/%s\n" dev.cfg > buildout.cfg
   $ python2.7 bootstrap.py
   $ bin/buildout

3. :ref:`runthetests`

4. :ref:`runtheapplication`

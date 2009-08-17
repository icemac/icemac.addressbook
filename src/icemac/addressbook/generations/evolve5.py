# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

__docformat__ = "reStructuredText"

import zope.app.generations.utility

import icemac.addressbook.interfaces
import icemac.addressbook.addressbook
import icemac.addressbook.person


generation = 5


def evolve(context):
    """Installs the the importer.
    """

    root = zope.app.generations.utility.getRootFolder(context)
    addressbooks = zope.app.generations.utility.findObjectsProviding(
        root, icemac.addressbook.interfaces.IAddressBook)
    for addressbook in addressbooks:
        icemac.addressbook.addressbook.create_address_book_infrastructure(
            addressbook)


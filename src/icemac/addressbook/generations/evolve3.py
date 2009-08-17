# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

__docformat__ = "reStructuredText"

import zope.app.generations.utility

import icemac.addressbook.interfaces
import icemac.addressbook.addressbook
import icemac.addressbook.person


generation = 3


person_created_with_set_site = icemac.addressbook.utils.set_site(
    icemac.addressbook.person.person_created)


def evolve(context):
    """Installs the authentication utility.
    """

    root = zope.app.generations.utility.getRootFolder(context)
    # persons need gocept.reference which needs a local utility stored in root

    # addressbooks
    addressbooks = zope.app.generations.utility.findObjectsProviding(
        root, icemac.addressbook.interfaces.IAddressBook)
    for addressbook in addressbooks:
        icemac.addressbook.addressbook.create_address_book_infrastructure(
            addressbook)


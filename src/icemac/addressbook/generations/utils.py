# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id$

import zope.app.generations.utility
import icemac.addressbook.interfaces
import icemac.addressbook.addressbook


def update_address_book_infrastructure(context):
    "Update the address book infrastructure (e. g. install new utilities)."
    root = zope.app.generations.utility.getRootFolder(context)
    addressbooks = zope.app.generations.utility.findObjectsProviding(
        root, icemac.addressbook.interfaces.IAddressBook)
    for addressbook in addressbooks:
        icemac.addressbook.addressbook.create_address_book_infrastructure(
            addressbook)


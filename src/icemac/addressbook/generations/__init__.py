# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$
"""Database initialisation and upgrading."""

import icemac.addressbook.addressbook
import icemac.addressbook.interfaces
import zope.app.generations.generations
import zope.app.generations.utility


GENERATION = 7

manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=GENERATION,
    generation=GENERATION,
    package_name='icemac.addressbook.generations')


# helper functions

def update_address_book_infrastructure(context):
    """Update the address book infrastructure (e. g. install new utilities)."""
    root = zope.app.generations.utility.getRootFolder(context)
    addressbooks = zope.app.generations.utility.findObjectsProviding(
        root, icemac.addressbook.interfaces.IAddressBook)
    for addressbook in addressbooks:
        icemac.addressbook.addressbook.create_address_book_infrastructure(
            addressbook)


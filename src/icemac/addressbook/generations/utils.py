# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id$

import zope.app.generations.utility
import icemac.addressbook.interfaces
import icemac.addressbook.addressbook
import logging


logger = logging.getLogger('evolve')


def evolve_addressbooks(func):
    "Decorator which evolves address books."
    def decorated(context):
        root = zope.app.generations.utility.getRootFolder(context)
        addressbooks = zope.app.generations.utility.findObjectsProviding(
            root, icemac.addressbook.interfaces.IAddressBook)
        for addressbook in addressbooks:
            logger.info('evolving %r' % addressbook)
            old_site = zope.site.hooks.getSite()
            try:
                zope.site.hooks.setSite(addressbook)
                func(addressbook)
            finally:
                zope.site.hooks.setSite(old_site)
    return decorated


@evolve_addressbooks
def update_address_book_infrastructure(addressbook):
    "Update the address book infrastructure (e. g. install new utilities)."
    icemac.addressbook.addressbook.create_address_book_infrastructure(
        addressbook)

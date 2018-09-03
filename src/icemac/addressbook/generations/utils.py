import functools
import icemac.addressbook.addressbook
import icemac.addressbook.interfaces
import logging
import zope.generations.utility


logger = logging.getLogger('evolve')


def evolve_addressbooks(func):
    """Decorator which evolves address books."""
    @functools.wraps(func)
    def decorated(context):
        root = zope.generations.utility.getRootFolder(context)
        addressbooks = zope.generations.utility.findObjectsProviding(
            root, icemac.addressbook.interfaces.IAddressBook)
        for addressbook in addressbooks:
            logger.info('evolving %r' % addressbook)
            old_site = zope.component.hooks.getSite()
            try:
                zope.component.hooks.setSite(addressbook)
                func(addressbook)
            finally:
                zope.component.hooks.setSite(old_site)
    return decorated


@evolve_addressbooks
def update_address_book_infrastructure(addressbook):
    """Update the address book infrastructure (e. g. install new utilities)."""
    icemac.addressbook.addressbook.create_address_book_infrastructure(
        addressbook)

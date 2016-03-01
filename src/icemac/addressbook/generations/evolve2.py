# -*- coding: latin-1 -*-
import icemac.addressbook.interfaces
import zope.catalog.interfaces
import zope.generations.utility


generation = 2


@icemac.addressbook.utils.set_site
def fix_kexword_index():
    catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
    catalog.updateIndex(catalog.get('keywords'))


def evolve(context):
    """The steet attribute of the postal address has been split into 2 fields.

    Update keyword index to fix bug that index was not updated, when
    keyword title changed.

    """
    root = zope.generations.utility.getRootFolder(context)

    # fix steet attribute
    addresses = zope.generations.utility.findObjectsProviding(
        root, icemac.addressbook.interfaces.IPostalAddress)
    for address in addresses:
        if address.street is None:
            continue
        old_street = address.street.split('\n')
        if len(old_street) > 1:
            address.address_prefix = old_street[0].strip()
            address.street = old_street[1].strip()

    # fix title index
    addressbooks = zope.generations.utility.findObjectsProviding(
        root, icemac.addressbook.interfaces.IAddressBook)
    for ab in addressbooks:
        fix_kexword_index(ab)

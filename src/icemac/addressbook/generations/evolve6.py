# -*- coding: latin-1 -*-
import icemac.addressbook.interfaces
import zope.generations.utility
import zope.catalog.interfaces
import zope.component


generation = 6


def evolve(context):
    """icemac.addressbook.interfaces.IKeywords.get_titles has been split into
    IKeywordTitles interface.
    """
    root = zope.generations.utility.getRootFolder(context)
    addressbooks = zope.generations.utility.findObjectsProviding(
        root, icemac.addressbook.interfaces.IAddressBook)
    for addressbook in addressbooks:
        catalog = zope.component.queryUtility(zope.catalog.interfaces.ICatalog,
                                              context=addressbook)

        catalog['keywords'].interface = (
            icemac.addressbook.interfaces.IKeywordTitles)

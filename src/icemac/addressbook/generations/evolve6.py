# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

__docformat__ = "reStructuredText"

import icemac.addressbook.interfaces
import icemac.addressbook.interfaces
import zope.app.generations.utility
import zope.catalog.interfaces
import zope.component


generation = 6


def evolve(context):
    """icemac.addressbook.interfaces.IKeywords.get_titles has been split into
    IKeywordTitles interface.
    """

    root = zope.app.generations.utility.getRootFolder(context)
    addressbooks = zope.app.generations.utility.findObjectsProviding(
        root, icemac.addressbook.interfaces.IAddressBook)
    for addressbook in addressbooks:
        catalog = zope.component.queryUtility(zope.catalog.interfaces.ICatalog,
                                              context=addressbook)

        catalog['keywords'].interface = (
            icemac.addressbook.interfaces.IKeywordTitles)


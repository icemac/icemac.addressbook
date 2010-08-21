# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id$

import icemac.addressbook.interfaces
import icemac.addressbook.namechooser.interfaces
import zope.app.generations.utility
import zope.catalog.interfaces
import zope.component
import zope.location.interfaces
import zope.proxy


def evolve(context):
    """Update persistent INameSuffix adapter for python 2.6: Provide
    ILocation interface, so zope.annotation.factory does not return a
    location proxy, where unicode function is not able to find __unicode__
    method any more.

    """

    root = zope.app.generations.utility.getRootFolder(context)
    addressbooks = zope.app.generations.utility.findObjectsProviding(
        root, icemac.addressbook.interfaces.IAddressBook)
    for addressbook in addressbooks:
        name_suffix = icemac.addressbook.namechooser.interfaces.INameSuffix(
            addressbook.entities)
        name_suffix = zope.proxy.getProxiedObject(name_suffix)
        zope.interface.directlyProvides(name_suffix,
                                        zope.location.interfaces.ILocation)
        name_suffix.__parent__ = addressbook.entities
        name_suffix.__name__ = 'icemac.namechooser.DontReuseNames.NameSuffix'

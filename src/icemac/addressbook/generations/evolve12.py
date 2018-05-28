import icemac.addressbook.interfaces
import icemac.addressbook.namechooser.interfaces
import zope.generations.utility
import zope.location.interfaces
import zope.proxy


def evolve(context):
    """Update persistent INameSuffix adapter for python 2.6:

    Provide ILocation interface, so zope.annotation.factory does not return a
    location proxy, where unicode function is not able to find __unicode__
    method any more.

    """
    root = zope.generations.utility.getRootFolder(context)
    addressbooks = zope.generations.utility.findObjectsProviding(
        root, icemac.addressbook.interfaces.IAddressBook)
    for addressbook in addressbooks:
        name_suffix = icemac.addressbook.namechooser.interfaces.INameSuffix(
            addressbook.entities)
        name_suffix = zope.proxy.getProxiedObject(name_suffix)
        zope.interface.directlyProvides(name_suffix,
                                        zope.location.interfaces.ILocation)
        name_suffix.__parent__ = addressbook.entities
        name_suffix.__name__ = 'icemac.namechooser.DontReuseNames.NameSuffix'

import icemac.addressbook.generations.utils
import icemac.addressbook.interfaces
import zope.annotation.interfaces
import zope.component
import zope.interface
import zope.location


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(ab):
    """Update order storage to make it metadata aware."""
    os = zope.component.getUtility(
        icemac.addressbook.interfaces.IOrderStorage)
    for ns in os.namespaces():
        storage = os.byNamespace(ns)
        zope.interface.alsoProvides(
            storage, zope.annotation.interfaces.IAttributeAnnotatable)
        zope.location.locate(storage, os._storage, ns)

import icemac.addressbook
import icemac.addressbook.browser.interfaces
import pkg_resources
import zope.component
import zope.contentprovider.interfaces
import zope.interface

class About(object):
    """View class for the about screen."""

    def version(self):
        return pkg_resources.get_distribution('icemac.addressbook').version


class CopyrightContentProvider(object):
    """Content provider for the copyright string."""
    zope.interface.implements(zope.contentprovider.interfaces.IContentProvider)
    zope.component.adapts(zope.interface.Interface,
                          icemac.addressbook.browser.interfaces.IAddressBookLayer,
                          zope.interface.Interface)

    def __init__(self, *args):
        pass

    def update(self):
        pass

    def render(self):
        return icemac.addressbook.copyright

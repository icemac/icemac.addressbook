import icemac.addressbook
import icemac.addressbook.browser.resource
import pkg_resources
import zope.contentprovider.provider


class About(object):
    """View class for the about screen."""

    def version(self):
        return pkg_resources.get_distribution('icemac.addressbook').version


class CopyrightContentProvider(
    zope.contentprovider.provider.ContentProviderBase):
    """Content provider for the copyright string."""

    def update(self):
        # Making sure css is rendered in layout.pt:
        icemac.addressbook.browser.resource.base_css.need()

    def render(self):
        return icemac.addressbook.copyright

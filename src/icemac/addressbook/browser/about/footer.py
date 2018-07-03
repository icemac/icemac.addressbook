# -*- coding: utf-8 -*-
import icemac.addressbook
import os
import z3c.menu.ready2go.item
import z3c.menu.ready2go.manager
import zope.contentprovider.provider
import zope.viewlet.manager


class CopyrightContentProvider(
        zope.contentprovider.provider.ContentProviderBase):
    """Content provider for the copyright string."""

    def render(self):
        return icemac.addressbook.copyright


class IFooterLinks(z3c.menu.ready2go.IGlobalMenu):
    """Marker interface for links to be shown in the footer."""


FooterLinksManager = zope.viewlet.manager.ViewletManager(
    'footer-links', IFooterLinks, bases=(
        z3c.menu.ready2go.manager.MenuManager,))


class FooterLink(z3c.menu.ready2go.item.GlobalMenuItem):
    """Base class for footer links.

    A special template is registered for this class.
    """

    @property
    def available(self):
        return bool(self.url)


class ImprintLink(FooterLink):
    """Imprint link in the footer."""

    @property
    def title(self):
        return os.environ.get('AB_LINK_IMPRINT_TEXT')

    @property
    def url(self):
        return os.environ.get('AB_LINK_IMPRINT_URL')


class DataprotectionLink(FooterLink):
    """Data protection link in the footer."""

    @property
    def title(self):
        return os.environ.get('AB_LINK_DATAPROTECTION_TEXT')

    @property
    def url(self):
        return os.environ.get('AB_LINK_DATAPROTECTION_URL')

# -*- coding: utf-8 -*-
import icemac.addressbook
import zope.contentprovider.provider


class CopyrightContentProvider(
        zope.contentprovider.provider.ContentProviderBase):
    """Content provider for the copyright string."""

    def render(self):
        return icemac.addressbook.copyright

# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Michael Howitz
from ..interfaces import IIconProviderInfo
import icemac.addressbook
import pkg_resources
import zope.contentprovider.provider


class About(object):
    """View class for the about screen."""

    def version(self):
        return pkg_resources.get_distribution('icemac.addressbook').version

    def icons(self):
        return zope.component.subscribers([None], IIconProviderInfo)


class CopyrightContentProvider(
    zope.contentprovider.provider.ContentProviderBase):
    """Content provider for the copyright string."""

    def render(self):
        return icemac.addressbook.copyright


class IconProviderInfo(object):
    """Infos about copyrights of icons used in the address book."""
    zope.interface.implements(IIconProviderInfo)

    name = NotImplemented
    url = NotImplemented

    def __init__(self, *ignored):
        pass


class DialogIcons(IconProviderInfo):
    name = u'VistaICO.com'
    url = (u'http://www.vistaico.com')


class AddressBookIcon(IconProviderInfo):
    name = u'Martin Šnajdr'
    url = (u'http://psd.tutsplus.com/tutorials/designing-tutorials/'
           u'create-a-custom-mac-osx-style-ring-binder-address-book-icon')

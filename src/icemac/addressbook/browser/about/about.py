# -*- coding: utf-8 -*-
from ..interfaces import IIconProviderInfo
from icemac.addressbook.i18n import _
import icemac.addressbook
import icemac.addressbook.browser.base
import pkg_resources
import zope.component
import zope.interface


class About(icemac.addressbook.browser.base.FlashView):
    """View class for the about screen."""

    title = _('About icemac.addressbook')

    def version(self):
        return pkg_resources.get_distribution('icemac.addressbook').version

    def icons(self):
        return zope.component.subscribers([None], IIconProviderInfo)


@zope.interface.implementer(IIconProviderInfo)
class IconProviderInfo(object):
    """Infos about copyrights of icons used in the address book."""

    name = NotImplemented
    url = NotImplemented

    def __init__(self, *ignored):
        pass


class DialogIcons(IconProviderInfo):
    """Copyright information of the icons used in the dialogs."""

    name = u'VistaICO.com'
    url = (u'http://www.vistaico.com')


class AddressBookIcon(IconProviderInfo):
    """Copyright information of the icon used for the address book."""

    name = u'Martin Šnajdr'
    url = (u'http://psd.tutsplus.com/tutorials/designing-tutorials/'
           u'create-a-custom-mac-osx-style-ring-binder-address-book-icon')

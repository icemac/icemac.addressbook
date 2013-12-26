from icemac.addressbook.i18n import _
import icemac.addressbook.browser.base
import icemac.addressbook.interfaces
import zope.dottedname.resolve
import zope.interface


class StartpageData(object):
    """Data of a startpage."""

    zope.interface.implements(icemac.addressbook.interfaces.IStartpageData)

    def __init__(self, iface_name, view, title):
        self.iface_name = iface_name
        self.view = view
        self.title = title

    def __call__(self, *args):
        return self


welcome = StartpageData(
    'icemac.addressbook.interfaces.IAddressBook', '@@welcome.html',
    _('Welcome page'))
person_list = StartpageData(
    'icemac.addressbook.interfaces.IAddressBook', '@@person-list.html',
    _('Person list'))
search = StartpageData(
    'icemac.addressbook.interfaces.IAddressBook', '@@search.html',
    _('Search'))


class Dispatch(icemac.addressbook.browser.base.BaseView):
    """Dispatch to the selected start page."""

    def __call__(self):
        iface_name, view = self.context.startpage
        iface = zope.dottedname.resolve.resolve(iface_name)
        target_url = self.url(iface(self.context), view)
        self.request.response.redirect(target_url)
        return ''

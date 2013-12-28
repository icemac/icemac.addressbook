from ..base import can_access_uri_part
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

    def _get_context_and_view_name(self, src):
        iface_name, view_name = src
        iface = zope.dottedname.resolve.resolve(iface_name)
        context = iface(self.context)
        return context, view_name

    def __call__(self):
        context, view_name = self._get_context_and_view_name(
            self.context.startpage)
        if not can_access_uri_part(context, self.request, view_name):
            context, view_name = self._get_context_and_view_name(
                icemac.addressbook.interfaces.DEFAULT_STARTPAGE_DATA)
        target_url = self.url(context, view_name)
        self.request.response.redirect(target_url)
        return ''

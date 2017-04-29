# -*- coding: utf-8 -*-
from icemac.addressbook.i18n import _
from icemac.addressbook.interfaces import IAddressBook
import icemac.addressbook.browser.base
import z3c.authviewlet.auth
import zope.component
import zope.contentprovider.provider
import zope.pluggableauth.interfaces
import zope.viewlet.viewlet


class AddressBookTitle(zope.contentprovider.provider.ContentProviderBase):
    """Content provider for the addressbook title string."""

    default_title = u'icemac.addressbook'

    def render(self):
        address_book = IAddressBook(self.context)
        if not IAddressBook.providedBy(address_book):
            return self.default_title
        return address_book.title or self.default_title


class LoggedInUserViewlet(
        zope.viewlet.viewlet.ViewletBase,
        icemac.addressbook.browser.base.BaseView):
    """Render info about the user currently logged-in.

    The info contains the log-in name and a link to the principal edit form if
    appropriate.
    """

    @property
    def available(self):
        return z3c.authviewlet.auth.authenticated(self.request.principal)

    def render(self):
        ab_principal = None
        principals = zope.component.queryUtility(
            zope.pluggableauth.interfaces.IAuthenticatorPlugin,
            name=u'icemac.addressbook.principals')
        request_principal = self.request.principal
        if principals is not None:
            ab_principal = principals.get(request_principal.id)
        if ab_principal is None:
            result = _('logged in as "${username}" -',
                       mapping=dict(username=request_principal.title))
        else:
            result = _('logged in as <a href="${url}">${username}</a> -',
                       mapping=dict(url=self.url(ab_principal, 'index.html'),
                                    username=ab_principal.login))
        return zope.i18n.translate(result, context=self.request)

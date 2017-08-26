import grokcore.component as grok
import icemac.addressbook.browser.base
import icemac.addressbook.browser.interfaces
import icemac.addressbook.interfaces
import zope.interface


class ISearchResultHandler(zope.interface.Interface):
    """I am a search result handler."""


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class Base(icemac.addressbook.browser.base.BaseView):
    """Base for search result handlers."""

    zope.interface.implements(ISearchResultHandler)

    @property
    def persons(self):
        addressbook = icemac.addressbook.interfaces.IAddressBook(None)
        return [addressbook[id] for id in self.session.get('person_ids', ())]


class SearchResultHandlerBreadcrumb(
        icemac.addressbook.browser.breadcrumb.ViewBreadcrumb):
    """Breadcrumb for search result handlers."""

    grok.adapts(
        ISearchResultHandler,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    @property
    def parent(self):
        return zope.component.getMultiAdapter(
            (icemac.addressbook.interfaces.IAddressBook(self.context),
             self.request), name='search.html')

# -*- coding: utf-8 -*-
from icemac.addressbook.i18n import _
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


class IBaseSelectionCount(zope.interface.Interface):
    """Base interface for the number of persons in selection."""

    # Copied from IPersonCount as inheriting from it leads to usage of wrong
    # adapter as the interface where the fields where initially defined on
    # is stored on the fields.
    count = zope.schema.Int(title=_(u'number of persons'), required=False)
    # Define this field in the interface inheriting from the base interface:
    # notes = zope.schema.TextLine(title=_(u'notes'), required=False)


def get_selected_person_ids(request):
    """Get the list of selected person ids from the session."""
    session = icemac.addressbook.browser.base.get_session(request)
    return session.get('person_ids', [])


class BaseSelectionCount(grok.Adapter):
    """Base class for an adapter to count persons in selection.

    Usage:
    * Inherit an interface from ``IBaseSelectionCount``.
    * Inherit from this class and provide an appropriate hint text.
    """

    grok.context(icemac.addressbook.interfaces.IAddressBook)
    grok.baseclass()

    def __init__(self, address_book):
        self.request = zope.globalrequest.getRequest()
        self.count = len(get_selected_person_ids(self.request))
        self.notes = u'🎁 Set and translate in child class'

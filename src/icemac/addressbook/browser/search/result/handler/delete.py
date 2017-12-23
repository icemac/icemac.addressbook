# -*- coding: utf-8 -*-
from icemac.addressbook.i18n import _
import icemac.addressbook.browser.base
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.search.result.handler.base
import icemac.addressbook.interfaces
import zope.globalrequest
import zope.i18n
import zope.interface
import zope.schema


class ISelectionCount(zope.interface.Interface):
    """Number of persons in selection."""

    # Copied from IPersonCount as inheriting from it leads to usage of wrong
    # adapter as the interface where the fields where initially defined on
    # is stored on the fields.
    count = zope.schema.Int(title=_(u'number of persons'), required=False)
    notes = zope.schema.TextLine(title=_(u'notes'), required=False)


def get_selected_person_ids(request):
    """Get the list of selected person ids from the session."""
    session = icemac.addressbook.browser.base.get_session(request)
    return session.get('person_ids', [])


@zope.component.adapter(icemac.addressbook.interfaces.IAddressBook)
@zope.interface.implementer(ISelectionCount)
class SelectionCount(object):
    """Adapter to count persons in selection."""

    def __init__(self, address_book):
        request = zope.globalrequest.getRequest()
        self.count = len(get_selected_person_ids(request))
        self.notes = zope.i18n.translate(
            _(u'You are not able to delete a person which is referenced. '
              u'You have to remove the reference before.'),
            context=request)


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground,
    icemac.addressbook.browser.search.result.handler.base.ISearchResultHandler)
class DeleteForm(icemac.addressbook.browser.base.BaseDeleteForm):
    """Delete selected persons."""

    title = _('Delete persons')
    label = _(u'Do you really want to delete the selected persons?')
    interface = ISelectionCount
    next_url = 'object'
    next_view = 'person-list.html'

    def _handle_action(self):
        ids = get_selected_person_ids(self.request)
        num_deleted = icemac.addressbook.browser.base.delete_persons(
            self.context, ids)
        self.status = _('Selected persons deleted: ${num}',
                        mapping=dict(num=num_deleted))
        self.redirect_to_next_url('object', self.next_view)


delete_view = icemac.addressbook.browser.menus.menu.SelectMenuItemOn(
    'delete_persons.html')

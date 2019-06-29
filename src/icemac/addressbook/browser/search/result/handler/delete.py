# -*- coding: utf-8 -*-
from .base import BaseSelectionCount
from .base import IBaseSelectionCount
from .base import ISearchResultHandler
from .base import get_selected_person_ids
from icemac.addressbook.i18n import _
import grokcore.component as grok
import icemac.addressbook.browser.base
import icemac.addressbook.browser.interfaces
import icemac.addressbook.interfaces
import zope.i18n
import zope.interface


class ISelectionCount(IBaseSelectionCount):
    """Number of persons in delete selection."""

    notes = zope.schema.TextLine(title=_(u'notes'), required=False)


@grok.implementer(ISelectionCount)
class DeleteSelectionCount(BaseSelectionCount):
    """Adapter to count persons in delete selection."""

    def __init__(self, address_book):
        super(DeleteSelectionCount, self).__init__(address_book)
        self.notes = zope.i18n.translate(
            _(u'You are not able to delete a person who is referenced. '
              u'You have to remove the reference before.'),
            context=self.request)


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground,
    ISearchResultHandler)
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

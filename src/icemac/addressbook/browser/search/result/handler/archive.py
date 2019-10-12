# -*- coding: utf-8 -*-
from .base import BaseSelectionCount
from .base import IBaseSelectionCount
from .base import ISearchResultHandler
from .base import get_selected_person_ids
from .manager import SearchResultHandler
from icemac.addressbook.i18n import _
import gocept.reference.interfaces
import grokcore.component as grok
import icemac.addressbook.browser.base
import icemac.addressbook.browser.interfaces
import icemac.addressbook.interfaces
import z3c.form.button
import zope.i18n
import zope.interface
import zope.security.proxy


class ISelectionCount(IBaseSelectionCount):
    """Number of persons in archive selection."""

    notes = zope.schema.TextLine(title=_(u'notes'), required=False)


@grok.implementer(ISelectionCount)
class ArchiveSelectionCount(BaseSelectionCount):
    """Adapter to count persons in archive selection."""

    def __init__(self, address_book):
        super(ArchiveSelectionCount, self).__init__(address_book)
        self.notes = zope.i18n.translate(
            _(u'You are not able to archive a person who is referenced. '
              u'You have to remove the reference before.'),
            context=self.request)


def archive_persons(address_book, ids):
    """Archive persons specified by their ID, but not users."""
    archived = 0
    # this list() call is needed as we might delete from the source of the ids:
    for name in list(ids):
        person = address_book[name]
        ref_target = gocept.reference.interfaces.IReferenceTarget(
            zope.security.proxy.getObject(person))
        if ref_target.is_referenced(recursive=False):
            # Persons which are referenced can't be archived using this
            # function. We check this here to avoid getting an error.
            continue
        person.archive()
        archived += 1
    return archived


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground,
    ISearchResultHandler)
class ArchiveForm(icemac.addressbook.browser.base._BaseConfirmForm):
    """Archive selected persons."""

    title = _('Archive persons')
    label = _('Do you really want to archive the selected persons?'
              ' Afterwards these persons can only be found in the archive,'
              ' neither be edited nor found using searches.')
    cancel_status_message = _('Archiving canceled.')
    interface = ISelectionCount
    next_url = 'object'
    next_view = 'person-list.html'
    z3c.form.form.extends(
        icemac.addressbook.browser.base._BaseConfirmForm, ignoreFields=True)

    @z3c.form.button.buttonAndHandler(_(u'Yes, archive'), name='action')
    def handleAction(self, action):
        self._handle_action()

    def _handle_action(self):
        ids = get_selected_person_ids(self.request)
        num_archived = archive_persons(self.context, ids)
        self.status = _('Selected persons archived: ${num}',
                        mapping=dict(num=num_archived))
        self.redirect_to_next_url('object', self.next_view)


archive_view = icemac.addressbook.browser.menus.menu.SelectMenuItemOn(
    'archive_persons.html')


class ArchiveSearchResultHandler(SearchResultHandler):
    """SearchResultHandler which is not available if archive is disabled."""

    @property
    def available(self):
        address_book = icemac.addressbook.interfaces.IAddressBook(None)
        return 'Archive' not in address_book.deselected_tabs

# -*- coding: utf-8 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.browser.base
import icemac.addressbook.browser.interfaces
import icemac.addressbook.export.sources
import icemac.addressbook.interfaces
import z3c.form.button
import z3c.ptcompat
import z3c.table.column
import zc.sourcefactory.interfaces
import zope.globalrequest
import zope.i18n
import zope.interface
import zope.schema
import zope.session.interfaces


class ISelectionCount(zope.interface.Interface):
    "Number of persons in selection."
    # Copied from IPersonCount as inheriting from it leads to usage of wrong
    # adapter as the interface where the fields where initially defined on
    # is stored on the fields.
    count = zope.schema.Int(title=_(u'number of persons'), required=False)
    notes = zope.schema.TextLine(title=_(u'notes'), required=False)



def get_selected_person_ids(request):
    """Get the list of selected person ids from the session."""
    session = zope.session.interfaces.ISession(request)[
        icemac.addressbook.interfaces.PACKAGE_ID]
    return session.get('person_ids', [])


class SelectionCount(object):
    "Adapter to count persons in selection."

    zope.interface.implements(ISelectionCount)
    zope.component.adapts(icemac.addressbook.interfaces.IAddressBook)

    def __init__(self, address_book):
        request = zope.globalrequest.getRequest()
        self.count = len(get_selected_person_ids(request))
        self.notes = zope.i18n.translate(
            _(u'Whether one of the selected persons is a user, it cannot get '
              u'deleted here, you have to delete the user before.'),
            context=request)


class DeleteForm(icemac.addressbook.browser.base.BaseDeleteForm):
    "Delete selected persons."

    label = _(u'Do you really want to delete the selected persons?')
    interface = ISelectionCount
    next_url = 'object'

    def _handle_delete(self):
        ids = get_selected_person_ids(self.request)
        len_ids = len(ids)
        icemac.addressbook.browser.base.delete_persons(
            self.context, ids)
        self.status = _('Selected persons deleted: ${num}',
                        mapping=dict(num=len_ids))
        self.redirect_to_next_url('object', '')

# -*- coding: latin-1 -*-
# Copyright (c) 2008-2013 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.browser.base
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.metadata
import icemac.addressbook.interfaces
import z3c.form.button
import zope.interface
import zope.size.interfaces


class EditForm(icemac.addressbook.browser.base.GroupEditForm):

    label = _(u'Edit address book data')
    interface = icemac.addressbook.interfaces.IAddressBook
    groups = (icemac.addressbook.browser.metadata.MetadataGroup,)
    next_url = 'object'
    next_view = '@@edit.html'

    @z3c.form.button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        super(EditForm, self).handleApply(self, action)

    @z3c.form.button.buttonAndHandler(
        _(u'Delete all persons in address book'), name='delete_content',
        condition=icemac.addressbook.browser.base.can_access(
            '@@delete_content.html'))
    def handleDeleteContent(self, action):
        self.redirect_to_next_url('object', '@@delete_content.html')


class DeleteForm(icemac.addressbook.browser.base.BaseDeleteForm):
    "Delete whole address book."

    label = _(u'Do you really want to delete this whole address book?')
    interface = icemac.addressbook.interfaces.IAddressBook
    field_names = ('title', )
    next_url = 'parent'

    def _do_delete(self):
        # delete users first
        principals = self.context.principals
        for name in list(principals.keys()):
            del principals[name]
        super(DeleteForm, self)._do_delete()


class PersonCount(object):
    "Adapter to count persons in address book."

    zope.interface.implements(
        icemac.addressbook.browser.interfaces.IPersonCount)
    zope.component.adapts(icemac.addressbook.interfaces.IAddressBook)

    def __init__(self, address_book):
        basic_unit, self.count = zope.size.interfaces.ISized(
            address_book).sizeForSorting()
        self.notes = zope.i18n.translate(
            _(u'The users inside this address book will not get deleted.'),
            context=zope.globalrequest.getRequest())


class DeleteContentForm(icemac.addressbook.browser.base.BaseDeleteForm):
    "Delete address book contents (aka persons)."

    label = _(
        u'Do you really want to delete all persons in this address book?')
    interface = icemac.addressbook.browser.interfaces.IPersonCount
    next_view = '@@edit.html'

    def _handle_delete(self):
        icemac.addressbook.browser.base.delete_persons(
            self.context, self.context.keys())
        self.status = _('Address book contents deleted.')
        self.redirect_to_next_url('object', 'person-list.html')

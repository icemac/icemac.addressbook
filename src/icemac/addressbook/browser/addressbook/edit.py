# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.browser.base
import icemac.addressbook.browser.base
import icemac.addressbook.interfaces
import z3c.form.button


class EditForm(icemac.addressbook.browser.base.BaseEditForm):

    label = _(u'Edit address book data')
    interface = icemac.addressbook.interfaces.IAddressBook
    next_url = 'object'
    next_view = '@@edit.html'

    @z3c.form.button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        super(EditForm, self).handleApply(self, action)

    @z3c.form.button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        self.status = self.noChangesMessage

    @z3c.form.button.buttonAndHandler(
        _(u'Delete whole address book'), name='delete_address_book',
        condition=icemac.addressbook.browser.base.can_access(
            '@@delete_address_book.html'))
    def handleDeleteAddressBook(self, action):
        self.redirect_to_next_url('object', '@@delete_address_book.html')


class DeleteForm(icemac.addressbook.browser.base.BaseDeleteForm):

    label = _(u'Do you really want to delete this whole address book?')
    interface = icemac.addressbook.interfaces.IAddressBook
    field_names = ('title', )
    next_view = '@@edit.html'
    next_view_after_delete = '@@index.html'

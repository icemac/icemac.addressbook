# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.browser.base
import icemac.addressbook.interfaces
import z3c.form.button
import zope.interface
import zope.schema
import zope.size.interfaces


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
        _(u'Delete all persons in address book'), name='delete_content',
        condition=icemac.addressbook.browser.base.can_access(
            '@@delete_content.html'))
    def handleDeleteContent(self, action):
        self.redirect_to_next_url('object', '@@delete_content.html')

    @z3c.form.button.buttonAndHandler(
        _(u'Delete whole address book'), name='delete_address_book',
        condition=icemac.addressbook.browser.base.can_access(
            '@@delete_address_book.html'))
    def handleDeleteAddressBook(self, action):
        self.redirect_to_next_url('object', '@@delete_address_book.html')


class DeleteForm(icemac.addressbook.browser.base.BaseDeleteForm):
    "Delete whole address book."

    label = _(u'Do you really want to delete this whole address book?')
    interface = icemac.addressbook.interfaces.IAddressBook
    field_names = ('title', )
    next_view = '@@edit.html'
    next_view_after_delete = '@@index.html'


class IPersonCount(zope.interface.Interface):
    "Number of persons in address book."

    count = zope.schema.Int(title=_(u'number of persons'))


class PersonCount(object):
    "Adapter to count persons in address book."

    zope.interface.implements(IPersonCount)
    zope.component.adapts(icemac.addressbook.interfaces.IAddressBook)

    def __init__(self, address_book):
        basic_unit, self.count = zope.size.interfaces.ISized(
            address_book).sizeForSorting()


class DeleteContentForm(icemac.addressbook.browser.base.BaseEditForm):
    "Delete address book contents (aka persons)."

    label = _(u'Do you really want to delete all persons in this address book?')
    interface = IPersonCount
    mode = z3c.form.interfaces.DISPLAY_MODE

    @z3c.form.button.buttonAndHandler(_(u'No, cancel'), name='cancel')
    def handleCancel(self, action):
        self.status = self.noChangesMessage
        self.redirect_to_next_url('object', '@@edit.html')

    @z3c.form.button.buttonAndHandler(_(u'Yes, delete'), name='delete')
    def handleDelete(self, action):
        for name in list(self.context.keys()):
            del self.context[name]
        self.redirect_to_next_url('object')

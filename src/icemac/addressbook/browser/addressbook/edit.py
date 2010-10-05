# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import gocept.reference.interfaces
import icemac.addressbook.browser.base
import icemac.addressbook.browser.metadata
import icemac.addressbook.interfaces
import z3c.form.button
import zope.interface
import zope.schema
import zope.security.proxy
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

    @z3c.form.button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        self.status = self.noChangesMessage

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


class IPersonCount(zope.interface.Interface):
    "Number of persons in address book."

    count = zope.schema.Int(title=_(u'number of persons'), required=False)
    notes = zope.schema.TextLine(title=_(u'notes'), required=False)

class PersonCount(object):
    "Adapter to count persons in address book."

    zope.interface.implements(IPersonCount)
    zope.component.adapts(icemac.addressbook.interfaces.IAddressBook)

    def __init__(self, address_book):
        basic_unit, self.count = zope.size.interfaces.ISized(
            address_book).sizeForSorting()
        self.notes = zope.i18n.translate(
            _(u'The users inside this address book will not get deleted.'),
            context=zope.globalrequest.getRequest())

class DeleteContentForm(icemac.addressbook.browser.base.BaseDeleteForm):
    "Delete address book contents (aka persons)."

    label = _(u'Do you really want to delete all persons in this address book?')
    interface = IPersonCount
    mode = z3c.form.interfaces.DISPLAY_MODE
    next_view = '@@edit.html'

    @z3c.form.button.buttonAndHandler(_(u'No, cancel'), name='cancel')
    def handleCancel(self, action):
        super(DeleteContentForm, self).handleCancel(self, action)

    @z3c.form.button.buttonAndHandler(_(u'Yes, delete'), name='delete')
    def handleDelete(self, action):
        for name in list(self.context.keys()):
            ref_target = gocept.reference.interfaces.IReferenceTarget(
                zope.security.proxy.getObject(self.context[name]))
            if ref_target.is_referenced(recursive=False):
                # Persons which are referenced by a user can't be
                # deleted using this function. We check this here to
                # avoid getting an error.
                continue
            del self.context[name]
        self.status = _('Address book contents deleted.')
        self.redirect_to_next_url('object', '')

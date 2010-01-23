# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import gocept.reference.interfaces
import icemac.addressbook.browser.base
import icemac.addressbook.interfaces
import z3c.form.button
import icemac.addressbook.browser.metadata


class AddForm(icemac.addressbook.browser.base.BaseAddForm):

    label = _(u'Add new keyword')
    interface = icemac.addressbook.interfaces.IKeyword
    class_ = icemac.addressbook.keyword.Keyword
    next_url = 'parent'


def can_delete_keyword(form):
    """Button condition telling if the displayed keyword is deleteable."""
    return (
        icemac.addressbook.browser.base.can_access('@@delete.html')(form)
        and
        not gocept.reference.interfaces.IReferenceTarget(
            form.context).is_referenced()
        )

class EditForm(icemac.addressbook.browser.base.GroupEditForm):

    groups = (icemac.addressbook.browser.metadata.MetadataGroup,)
    label = _(u'Edit keyword')
    interface = icemac.addressbook.interfaces.IKeyword
    next_url = 'parent'

    def applyChanges(self, data):
        # GroupForm has its own applyChanges but we need the one from
        # BaseEditForm here as inside the goups no changes are made
        # but there is a subscriber which raises an error which is
        # handled by BaseEditForm.
        return icemac.addressbook.browser.base.BaseEditForm.applyChanges(
            self, data)

    @z3c.form.button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        # because we define a new action we have to duplicate the
        # existing action because otherwise we'll loose it.
        super(EditForm, self).handleApply(self, action)

    @z3c.form.button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        self.status = self.noChangesMessage

    @z3c.form.button.buttonAndHandler(
        _(u'Delete'), name='delete', condition=can_delete_keyword)
    def handleDelete(self, action):
        self.redirect_to_next_url('object', '@@delete.html')


class DeleteForm(icemac.addressbook.browser.base.BaseDeleteForm):
    label = _(u'Do you really want to delete this keyword?')
    interface = icemac.addressbook.interfaces.IKeyword
    field_names = ('title', )

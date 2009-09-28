# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import gocept.reference.interfaces
import icemac.addressbook.browser.base
import icemac.addressbook.interfaces
import z3c.form.button
import zope.component
import zope.traversing.browser.interfaces


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

class EditForm(icemac.addressbook.browser.base.BaseEditForm):

    label = _(u'Edit keyword')
    interface = icemac.addressbook.interfaces.IKeyword
    next_url = 'parent'

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
        url = zope.component.getMultiAdapter(
            (self.context, self.request),
            zope.traversing.browser.interfaces.IAbsoluteURL)()
        self.request.response.redirect(url + '/@@delete.html')


class DeleteForm(icemac.addressbook.browser.base.BaseDeleteForm):
    label = _(u'Do you really want to delete this keyword?')
    interface = icemac.addressbook.interfaces.IKeyword
    field_names = ('title', )

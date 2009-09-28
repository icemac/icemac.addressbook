# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import MessageFactory as _
import z3c.form.group
import z3c.form.interfaces
import z3c.form.field
import zope.dublincore.interfaces
import zope.component


class ModifiedGroup(z3c.form.group.Group):
    "Group to display modification information."

    label = _('last modification information')
    mode = z3c.form.interfaces.DISPLAY_MODE
    fields = z3c.form.field.Fields(
        zope.dublincore.interfaces.IDCTimes).select('modified')

    def updateWidgets(self):
        '''See interfaces.IForm'''
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()),
            z3c.form.interfaces.IWidgets)
        for attrName in ('ignoreRequest', 'ignoreContext', 'ignoreReadonly'):
            value = getattr(self.parentForm.widgets, attrName)
            setattr(self.widgets, attrName, value)
        # we need the value from the group here, not the one from the
        # parent form
        self.widgets.mode = self.mode
        self.widgets.update()


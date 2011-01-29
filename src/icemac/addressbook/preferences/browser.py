# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.browser.resource
import z3c.preference.browser


class EditForm(icemac.addressbook.browser.base.BaseEditFormWithCancel,
               z3c.preference.browser.EditForm):
    """Preference EditForm which uses addressbook's form CSS."""

    next_url = 'site'
    __init__ = z3c.preference.browser.EditForm.__init__
    fields = z3c.preference.browser.EditForm.fields

    def update(self):
        icemac.addressbook.browser.resource.form_css.need()
        super(EditForm, self).update()

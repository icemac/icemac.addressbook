# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.browser.resource
import z3c.preference.browser
import icemac.addressbook.browser.base


class EditForm(icemac.addressbook.browser.base.BaseEditForm,
               z3c.preference.browser.CategoryEditForm):
    """Preference EditForm which uses address book's form CSS."""

    next_url = 'site'
    __init__ = z3c.preference.browser.CategoryEditForm.__init__

    def update(self):
        icemac.addressbook.browser.resource.form_css.need()
        super(EditForm, self).update()

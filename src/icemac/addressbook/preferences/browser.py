# -*- coding: utf-8 -*-
# Copyright (c) 2010 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.browser.resource
import z3c.preference.browser


class EditForm(z3c.preference.browser.EditForm):
    """Preference EditForm which uses addressbook's form CSS."""

    def update(self):
        icemac.addressbook.browser.resource.form_css.need()
        super(EditForm, self).update()

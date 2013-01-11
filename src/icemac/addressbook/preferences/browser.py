# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Michael Howitz
# See also LICENSE.txt

import fanstatic
import icemac.addressbook.browser.base
import icemac.addressbook.browser.resource
import js.jqueryui
import z3c.preference.browser


lib = fanstatic.Library('prefs', 'resources')
css = fanstatic.Resource(
        lib, 'prefs.css',
        depends=[icemac.addressbook.browser.resource.form_css])
js = fanstatic.Resource(lib, 'prefs.js', depends=[js.jqueryui.jqueryui])


class EditForm(icemac.addressbook.browser.base.BaseEditForm,
               z3c.preference.browser.CategoryEditForm):
    """Preference EditForm which uses address book's form CSS."""

    next_url = 'site'
    next_view = 'person-list.html'
    __init__ = z3c.preference.browser.CategoryEditForm.__init__

    def update(self):
        css.need()
        js.need()
        super(EditForm, self).update()

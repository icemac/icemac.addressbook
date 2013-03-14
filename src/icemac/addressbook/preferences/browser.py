# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Michael Howitz
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
js = fanstatic.Resource(lib, 'prefs.js', depends=[js.jqueryui.effects_fade])


class CategoryEditForm(icemac.addressbook.browser.base.BaseEditForm,
                       z3c.preference.browser.CategoryEditForm):
    """Preference CategoryEditForm which uses CSS of address book."""

    next_url = 'site'
    next_view = 'person-list.html'
    __init__ = z3c.preference.browser.CategoryEditForm.__init__

    def update(self):
        css.need()
        js.need()
        super(CategoryEditForm, self).update()


class PrefGroupEditForm(icemac.addressbook.browser.base.BaseEditForm,
                        z3c.preference.browser.EditForm):
    """Preference group EditForm which uses CSS of address book."""

    __init__ = z3c.preference.browser.EditForm.__init__

    def redirect_to_next_url(self):
        # Stay on form but reload the values from database in case of
        # cancel:
        self.request.response.redirect(self.request.URL)

# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Michael Howitz
# See also LICENSE.txt
import icemac.addressbook.browser.base
import z3c.preference.browser


class CategoryEditForm(icemac.addressbook.browser.base.BaseEditForm,
                       z3c.preference.browser.CategoryEditForm):
    """Preference CategoryEditForm which uses CSS of address book."""

    id = 'prefs-category-edit-form'
    next_url = 'site'
    next_view = 'person-list.html'
    __init__ = z3c.preference.browser.CategoryEditForm.__init__


class PrefGroupEditForm(icemac.addressbook.browser.base.BaseEditForm,
                        z3c.preference.browser.EditForm):
    """Preference group EditForm which uses CSS of address book."""

    __init__ = z3c.preference.browser.EditForm.__init__

    def redirect_to_next_url(self):
        # Stay on form but reload the values from database in case of
        # cancel:
        self.request.response.redirect(self.request.URL)

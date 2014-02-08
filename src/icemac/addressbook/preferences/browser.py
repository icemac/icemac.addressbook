# -*- coding: utf-8 -*-
# Copyright (c) 2010-2014 Michael Howitz
# See also LICENSE.txt
import icemac.addressbook.browser.base
import z3c.preference.browser
import zope.interface
import icemac.addressbook.browser.interfaces


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class CategoryEditForm(icemac.addressbook.browser.base.BaseEditForm,
                       z3c.preference.browser.CategoryEditForm):
    """Preference CategoryEditForm which uses CSS of address book."""

    id = 'prefs-category-edit-form'
    next_url = 'site'
    next_view = 'person-list.html'
    __init__ = z3c.preference.browser.CategoryEditForm.__init__


# Not implementing IAddressBookBackground here as this view is used in
# icemac.ab.calendar, too.
class PrefGroupEditForm(icemac.addressbook.browser.base.BaseEditForm,
                        z3c.preference.browser.EditForm):
    """Preference group EditForm which uses CSS of address book."""

    __init__ = z3c.preference.browser.EditForm.__init__

    def redirect_to_next_url(self):
        # Stay on form but reload the values from database in case of
        # cancel:
        self.request.response.redirect(self.request.URL)

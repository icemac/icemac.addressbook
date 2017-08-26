# -*- coding: utf-8 -*-
import icemac.addressbook.browser.base
import icemac.addressbook.browser.interfaces
import z3c.preference.browser
import zope.interface


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class CategoryEditForm(icemac.addressbook.browser.base.BaseEditForm,
                       z3c.preference.browser.CategoryEditForm):
    """Preference CategoryEditForm which uses CSS of address book."""

    id = 'prefs-category-edit-form'
    next_url = 'site'
    next_view = 'person-list.html'

    def __init__(self, *args, **kw):
        z3c.preference.browser.CategoryEditForm.__init__(self, *args, **kw)
        self.title = self.label
        # Reset label to omit it from rendering:
        self.label = u''


# Not implementing IAddressBookBackground here as this view is used in
# icemac.ab.calendar, too.
class PrefGroupEditForm(icemac.addressbook.browser.base.BaseEditForm,
                        z3c.preference.browser.EditForm):
    """Preference group EditForm which uses CSS of address book."""

    def __init__(self, *args, **kw):
        z3c.preference.browser.EditForm.__init__(self, *args, **kw)
        self.title = self.label
        # Reset label to omit it from rendering:
        self.label = u''

    def redirect_to_next_url(self):
        # Stay on form but reload the values from database in case of
        # cancel:
        self.request.response.redirect(self.request.URL)

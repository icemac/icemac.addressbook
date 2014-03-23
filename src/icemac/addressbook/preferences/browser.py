# -*- coding: utf-8 -*-
# Copyright (c) 2010-2014 Michael Howitz
# See also LICENSE.txt
import grokcore.component as grok
import icemac.addressbook.browser.base
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.menus.menu
import z3c.menu.ready2go.checker
import z3c.menu.ready2go.item
import z3c.preference.browser
import zope.interface
import zope.preference.interfaces


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


class PreferencesMenuItem(z3c.menu.ready2go.item.SiteMenuItem):
    """Menu item for the preferences tab in the site menu."""


class PreferencesMenuItemSelectedChecker(
        z3c.menu.ready2go.checker.TrueSelectedChecker,
        grok.MultiAdapter):
    """Selected checker for the Preferences menu item in the site menu."""

    grok.adapts(zope.interface.Interface,
                icemac.addressbook.browser.interfaces.IAddressBookLayer,
                zope.interface.Interface,
                icemac.addressbook.browser.menus.menu.MainMenu,
                PreferencesMenuItem)

    @property
    def selected(self):
        return zope.preference.interfaces.IPreferenceGroup.providedBy(
            self.context)

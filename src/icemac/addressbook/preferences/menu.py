# -*- coding: utf-8 -*-
import grokcore.component as grok
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.menus.menu
import z3c.menu.ready2go.checker
import z3c.menu.ready2go.item
import zope.interface
import zope.preference.interfaces


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

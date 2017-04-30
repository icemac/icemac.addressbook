from .interfaces import ISearchMenuItemOn
import grokcore.component as grok
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.menus.menu
import z3c.menu.ready2go
import z3c.menu.ready2go.item
import z3c.menu.ready2go.manager
import zope.interface
import zope.viewlet.manager


class SearchMenuItem(z3c.menu.ready2go.item.SiteMenuItem):
    """Site menu item for the search tab."""


class SearchMenuItemSelectedChecker(
        icemac.addressbook.browser.menus.menu.SubscriberSelectedChecker):
    """Selected checker for the search menu item in the site menu."""

    grok.adapts(zope.interface.Interface,
                icemac.addressbook.browser.interfaces.IAddressBookLayer,
                zope.interface.Interface,
                icemac.addressbook.browser.menus.menu.MainMenu,
                SearchMenuItem)
    subscriber_interface = ISearchMenuItemOn


# Menu on the search page displaying the different search kinds:
SearchMenu = zope.viewlet.manager.ViewletManager(
    'left', z3c.menu.ready2go.IContextMenu,
    bases=(z3c.menu.ready2go.manager.MenuManager,))

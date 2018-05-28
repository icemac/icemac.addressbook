from .interfaces import IMasterData, IMasterDataMenuItemOn
import grokcore.component as grok
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.menus.menu
import z3c.menu.ready2go.item
import z3c.menu.ready2go.manager
import zope.interface
import zope.viewlet.manager


class MasterDataMenuItem(z3c.menu.ready2go.item.SiteMenuItem):
    """Site menu item for the master data tab."""


class MasterDataMenuItemSelectedChecker(
        icemac.addressbook.browser.menus.menu.SubscriberSelectedChecker):
    """Selected checker for the master data menu item in the site menu."""

    grok.adapts(zope.interface.Interface,
                icemac.addressbook.browser.interfaces.IAddressBookLayer,
                zope.interface.Interface,
                icemac.addressbook.browser.menus.menu.MainMenu,
                MasterDataMenuItem)
    subscriber_interface = IMasterDataMenuItemOn


# Menu on the master date page displaying the different master data edit links:
MasterDataManager = zope.viewlet.manager.ViewletManager(
    'master-data', IMasterData, bases=(
        z3c.menu.ready2go.manager.MenuManager,))

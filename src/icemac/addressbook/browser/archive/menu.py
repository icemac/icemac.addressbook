import grokcore.component as grok
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.menus.menu
import icemac.addressbook.interfaces
import z3c.menu.ready2go.checker
import z3c.menu.ready2go.item
import zope.interface


class ArchiveMenuItem(z3c.menu.ready2go.item.SiteMenuItem):
    """Menu item for the archive tab in the site menu."""


class ArchiveMenuItemSelectedChecker(
        z3c.menu.ready2go.checker.TrueSelectedChecker,
        grok.MultiAdapter):
    """Selected checker for the archive menu item in the site menu."""

    grok.adapts(zope.interface.Interface,
                icemac.addressbook.browser.interfaces.IAddressBookLayer,
                zope.interface.Interface,
                icemac.addressbook.browser.menus.menu.MainMenu,
                ArchiveMenuItem)

    @property
    def selected(self):
        if icemac.addressbook.interfaces.IArchive.providedBy(self.context):
            return True
        if icemac.addressbook.interfaces.IArchivedPerson.providedBy(
                self.context):
            return True
        return False

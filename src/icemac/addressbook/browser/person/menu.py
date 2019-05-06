import grokcore.component as grok
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.menus.menu
import z3c.menu.ready2go.checker
import z3c.menu.ready2go.item
import zope.interface


class PersonListMenuItem(z3c.menu.ready2go.item.SiteMenuItem):
    """Sitem menu item for the person list."""


class PersonListSelectedChecker(
        z3c.menu.ready2go.checker.ViewNameSelectedChecker,
        grok.MultiAdapter):
    """Selected checker of person list for the site menu."""

    grok.adapts(zope.interface.Interface,
                icemac.addressbook.browser.interfaces.IAddressBookLayer,
                zope.interface.Interface,
                icemac.addressbook.browser.menus.menu.MainMenu,
                PersonListMenuItem)

    @property
    def selected(self):
        if super(PersonListSelectedChecker, self).selected:
            return True
        if self.view.__name__ == 'addPerson.html':
            return True
        if icemac.addressbook.interfaces.IArchivedPerson.providedBy(
                self.context):
            return False
        if icemac.addressbook.interfaces.IPerson.providedBy(self.context):
            return True
        return False

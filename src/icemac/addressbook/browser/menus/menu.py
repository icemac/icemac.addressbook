# -*- coding: latin-1 -*-
# Copyright (c) 2008-2014 Michael Howitz
# See also LICENSE.txt
import icemac.addressbook.browser.menus.interfaces
import z3c.menu.ready2go.manager
import zope.viewlet.manager
import zope.viewlet.viewlet


MainMenu = zope.viewlet.manager.ViewletManager(
    'main-menu', icemac.addressbook.browser.menus.interfaces.IMainMenu,
    bases=(z3c.menu.ready2go.manager.MenuManager,))


def getWeight((name, viewlet)):
    view_name = viewlet.viewName
    if view_name.startswith('@@'):
        # remove starting @@
        view_name = view_name[2:]
    view = zope.component.getMultiAdapter(
        (viewlet.context, viewlet.request), name=view_name)
    interface = getattr(view, 'interface', None)
    if interface is None:
        interface = getattr(view, 'interface_for_menu', None)
    assert interface is not None, (
        'View %r does neither have a non-null value on `interface` nor '
        'on `interface_for_menu` attribute. But this is needed to compute '
        'the AddMenu contents.' % view)
    entity = icemac.addressbook.interfaces.IEntity(interface)
    order = zope.component.getUtility(
        icemac.addressbook.interfaces.IEntityOrder)
    try:
        return order.get(entity)
    except (KeyError, zope.component.ComponentLookupError):
        # The entity is not known in the order or we are outside an address
        # book.
        return 0


class OrdersWeightMenuManager(z3c.menu.ready2go.manager.MenuManager):
    "Menu manager which uses address_book.orders as weight."

    def sort(self, viewlets):
        return sorted(viewlets, key=getWeight)


class EmptyViewlet(zope.viewlet.viewlet.ViewletBase):
    """Helper class for AlwaysRenderTemplateManager."""

    def render(self):
        return u''

EMPTY_VIEWLET = EmptyViewlet(None, None, None, None)


class AlwaysRenderTemplateManager(OrdersWeightMenuManager):
    """Manager rendering template even there are no viewlets."""

    def update(self):
        super(AlwaysRenderTemplateManager, self).update()
        self.have_viewlets = bool(self.viewlets)
        if not self.have_viewlets:
            # Trick `render` method to render manager's template:
            self.viewlets.append(EMPTY_VIEWLET)


AddMenu = zope.viewlet.manager.ViewletManager(
    'add-menu', icemac.addressbook.browser.menus.interfaces.IAddMenu,
    bases=(AlwaysRenderTemplateManager,))

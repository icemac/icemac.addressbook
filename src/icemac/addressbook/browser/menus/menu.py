# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id$

import zope.viewlet.manager
import icemac.addressbook.browser.menus.interfaces
import z3c.menu.ready2go.manager

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
    entity = icemac.addressbook.interfaces.IEntity(view.interface)
    orders = zope.component.queryUtility(
        icemac.addressbook.interfaces.IOrderStorage)
    if orders is None:
        # outside address book
        return 0
    try:
        return orders.get(entity.name, icemac.addressbook.interfaces.ENTITIES)
    except ValueError:
        # there is no entity for the interface
        return 0


class OrdersWeightMenuManager(z3c.menu.ready2go.manager.MenuManager):
    "Menu manager which uses address_book.orders as weight."

    def sort(self, viewlets):
        return sorted(viewlets, key=getWeight)


AddMenu = zope.viewlet.manager.ViewletManager(
    'add-menu', icemac.addressbook.browser.menus.interfaces.IAddMenu,
    bases=(OrdersWeightMenuManager,))

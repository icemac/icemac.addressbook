# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

import zope.viewlet.manager
import icemac.addressbook.browser.menus.interfaces
import z3c.menu.ready2go.manager

MainMenu = zope.viewlet.manager.ViewletManager(
    'main-menu', icemac.addressbook.browser.menus.interfaces.IMainMenu,
    bases=(z3c.menu.ready2go.manager.MenuManager,))

AddMenu = zope.viewlet.manager.ViewletManager(
    'add-menu', icemac.addressbook.browser.menus.interfaces.IAddMenu,
    bases=(z3c.menu.ready2go.manager.MenuManager,))

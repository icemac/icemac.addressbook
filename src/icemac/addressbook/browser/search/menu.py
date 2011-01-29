# -*- coding: latin-1 -*-
# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id$

import zope.viewlet.manager
import z3c.menu.ready2go
import z3c.menu.ready2go.manager


SearchMenu = zope.viewlet.manager.ViewletManager(
    'left', z3c.menu.ready2go.IContextMenu,
    bases=(z3c.menu.ready2go.manager.MenuManager,))

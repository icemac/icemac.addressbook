# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

import z3c.menu.ready2go
import z3c.menu.ready2go.manager
import zope.viewlet.manager


class IMasterData(z3c.menu.ready2go.ISiteMenu):
    """Containing viewlets which provide links to edit master data."""


MasterDataManager = zope.viewlet.manager.ViewletManager(
    'master-data', IMasterData, bases=(
        z3c.menu.ready2go.manager.MenuManager,))

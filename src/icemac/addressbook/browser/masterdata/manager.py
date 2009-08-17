# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import zope.viewlet.interfaces
import zope.viewlet.manager


class IMasterData(zope.viewlet.interfaces.IViewletManager):
    """Containing viewlets which provide links to edit master data."""


MasterDataManager = zope.viewlet.manager.ViewletManager(
    'master-data', IMasterData, bases=(
        zope.viewlet.manager.WeightOrderedViewletManager,))

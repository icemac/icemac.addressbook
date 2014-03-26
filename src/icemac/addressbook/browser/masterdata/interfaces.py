# Copyright (c) 2009-2014 Michael Howitz
# See also LICENSE.txt
import z3c.menu.ready2go
import zope.interface


class IMasterData(z3c.menu.ready2go.ISiteMenu):
    """Menu containing viewlets which provide links to edit the master data."""


class IMasterDataMenuItemOn(zope.interface.Interface):
    """List of view names for which the master data menu item in the main
       navigation should be highlighted."""

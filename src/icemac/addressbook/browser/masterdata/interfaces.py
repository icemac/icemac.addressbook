import z3c.menu.ready2go
import zope.interface


class IMasterData(z3c.menu.ready2go.ISiteMenu):
    """Menu containing viewlets which provide links to edit the master data."""


class IMasterDataMenuItemOn(zope.interface.Interface):
    """List of view names.

    For these names the master data menu item in the main navigation should be
    highlighted.
    """

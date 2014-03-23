# -*- coding: latin-1 -*-
# Copyright (c) 2008-2014 Michael Howitz
# See also LICENSE.txt
# $Id$

import z3c.menu.ready2go
import zope.interface
import zope.viewlet.interfaces


class ISearchMenu(z3c.menu.ready2go.ISiteMenu):
    """Search menu."""


class ISearchForm(zope.viewlet.interfaces.IViewletManager):
    """Search form manager."""


class ISearchResult(zope.viewlet.interfaces.IViewletManager):
    """Search form manager."""


class ISearch(zope.interface.Interface):
    """A search."""

    def search(**kw):
        "Search for given keyword arguments and return iterable of results."


class ISearchMenuItemOn(zope.interface.Interface):
    """List of view names for which the search menu item in the main navigation
       should be highlighted."""

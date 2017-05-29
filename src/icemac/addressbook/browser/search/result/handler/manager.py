import icemac.addressbook.browser.search.base
import icemac.addressbook.sources
import z3c.menu.ready2go
import z3c.menu.ready2go.item
import z3c.menu.ready2go.manager
import zope.viewlet.manager


class ISearchResultHandlers(z3c.menu.ready2go.ISiteMenu):
    """Collection of search result handlers."""


SearchResultHandlerManager = zope.viewlet.manager.ViewletManager(
    'search-result-handlers', ISearchResultHandlers, bases=(
        z3c.menu.ready2go.manager.MenuManager,))


source = icemac.addressbook.sources.SiteMenuSource(
    icemac.addressbook.browser.search.base.BaseView, SearchResultHandlerManager
)


class SearchResultHandler(z3c.menu.ready2go.item.SiteMenuItem):
    """Specialized menu item to be used in SearchResultHandlerManager."""

    def __eq__(self, other):
        """Each handler has a unique viewName, usable for comparison."""
        if not isinstance(other, SearchResultHandler):
            return False
        return self.viewName == other.viewName

    def __hash__(self):
        return hash(self.viewName)

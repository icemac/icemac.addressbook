"""Search by `name` index."""
from icemac.addressbook.i18n import _
from icemac.addressbook.interfaces import IPerson
from icemac.addressbook.interfaces import ISchemaName
import icemac.addressbook.browser.menus.menu
import icemac.addressbook.browser.search.base
import zope.catalog.interfaces
import zope.component
import zope.index.text.parsetree
import zope.interface
import zope.schema


class SearchView(icemac.addressbook.browser.search.base.BaseView):
    """View which represents the name search."""

    title = _('Name search')
    form_explanation = _(
        'You may use wildcards in this search: Use ? for a single character '
        'or * for multiple characters.')


class ISearchFields(zope.interface.Interface):
    """Fields displayed in the search form."""

    search_term = zope.schema.TextLine(
        title=_('Name of a person'),
        description=_('You may use ? as wildcard for a single character or * '
                      'as wildcard for multiple characters.'))


class SearchForm(icemac.addressbook.browser.search.base.BaseSearchForm):

    interface = ISearchFields


@zope.component.adapter(SearchView)
class Search(icemac.addressbook.browser.search.base.BaseSearch):
    """The actual search."""

    def search(self, search_term):
        catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
        try:
            result_set = catalog.searchResults(
                name=search_term,
                schema_name={'any_of': [ISchemaName(IPerson).schema_name]}
            )
        except zope.index.text.parsetree.ParseError:
            result_set = ()
        return result_set


view = icemac.addressbook.browser.menus.menu.SelectMenuItemOn(
    'name_search.html')

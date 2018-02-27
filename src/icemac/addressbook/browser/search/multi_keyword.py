from icemac.addressbook.i18n import _
from icemac.addressbook.interfaces import IPerson
from icemac.addressbook.interfaces import ISchemaName
import collections
import icemac.addressbook.browser.menus.menu
import icemac.addressbook.browser.search.base
import icemac.addressbook.sources
import zope.catalog.interfaces
import zope.component
import zope.interface
import zope.schema


class SearchView(icemac.addressbook.browser.search.base.BaseView):
    """View representing multi-keyword search."""

    title = _('Keyword search')
    form_explanation = _(
        'Select requested keywords from the list popping up when selecting'
        ' the keywords control.')


class SearchTermConcatenationSource(
        icemac.addressbook.sources.TitleMappingSource):

    _mapping = collections.OrderedDict(
        (('and', _(u'search-and', default=u'and')),
         ('or', _(u'search-or', default=u'or'))))


class ISearchForm(zope.interface.Interface):

    concat = zope.schema.Choice(
        title=_(u'search term concatenation'),
        source=SearchTermConcatenationSource(), default='and')

    keywords = zope.schema.Set(
        title=_('keywords'), required=False,
        value_type=zope.schema.Choice(
            title=_('keywords'),
            source=icemac.addressbook.interfaces.keyword_source))


class SearchForm(icemac.addressbook.browser.search.base.BaseSearchForm):

    interface = ISearchForm


concat_mapping = {'and': 'all_of',
                  'or': 'any_of'}


@zope.component.adapter(SearchView)
class Search(icemac.addressbook.browser.search.base.BaseSearch):
    """Search for a multiple keywords."""

    def search(self, concat, keywords):
        concat = concat_mapping[concat]
        keywords = tuple(x.title for x in keywords)
        catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
        result_set = catalog.searchResults(
            keywords={concat: keywords},
            schema_name={'any_of': [ISchemaName(IPerson).schema_name]},
        )
        return result_set


view = icemac.addressbook.browser.menus.menu.SelectMenuItemOn(
    'multi_keyword.html')

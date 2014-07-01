# -*- coding: utf-8 -*-
# Copyright (c) 2010-2014 Michael Howitz
# See also LICENSE.txt
from icemac.addressbook.i18n import _
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
    form_explanation = _(
        'The keywords you want to search for have to be in the right box. '
        'Use the arrow buttons to move them.')


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


class Search(icemac.addressbook.browser.search.base.BaseSearch):
    """Search for a muliple keyword."""

    zope.component.adapts(SearchView)

    def search(self, concat, keywords):
        concat = concat_mapping[concat]
        keywords = tuple(x.title for x in keywords)
        catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
        result_set = catalog.searchResults(keywords={concat: keywords})
        return result_set


view = icemac.addressbook.browser.menus.menu.SelectMenuItemOn(
    'multi_keyword.html')

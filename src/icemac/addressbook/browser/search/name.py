# -*- coding: utf-8 -*-
# Copyright (c) 2011 Michael Howitz
# See also LICENSE.txt
"""Search by `name` index."""
from icemac.addressbook.i18n import _
import icemac.addressbook.browser.search.base
import icemac.addressbook.browser.search.interfaces
import zope.catalog.interfaces
import zope.component
import zope.interface
import zope.schema


class SearchView(icemac.addressbook.browser.search.base.BaseView):
    """View which represents the name search."""
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


class Search(icemac.addressbook.browser.search.base.BaseSearch):
    """The actual search."""

    zope.component.adapts(SearchView)

    def search(self, search_term):
        catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
        result_set = catalog.searchResults(name=search_term)
        return result_set

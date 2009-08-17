# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

import zope.catalog.interfaces
import zope.component
import zope.interface
import zope.schema

import icemac.addressbook.browser.search.base
import icemac.addressbook.sources
import icemac.addressbook.browser.search.interfaces

from icemac.addressbook.i18n import MessageFactory as _


class SearchView(icemac.addressbook.browser.search.base.BaseView):
    pass


class Search(object):
    """Search for a single keyword."""
    zope.component.adapts(SearchView)
    zope.interface.implements(
        icemac.addressbook.browser.search.interfaces.ISearch)

    def __init__(self, *args):
        pass

    def search(self, keyword):
        keyword = keyword.title
        catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
        result_set = catalog.searchResults(keywords={'any_of': (keyword, )})
        return result_set


class ISingleSimpleKeyword(zope.interface.Interface):

    keyword = zope.schema.Choice(
        title=_('keyword'),
        source=icemac.addressbook.sources.keyword_source)


class SearchForm(icemac.addressbook.browser.search.base.BaseSearchForm):

    interface = ISingleSimpleKeyword

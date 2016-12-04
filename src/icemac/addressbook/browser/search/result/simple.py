# -*- coding: utf-8 -*-
import icemac.addressbook.browser.search.result.base


class PersonTable(
        icemac.addressbook.browser.search.result.base.BasePersonTable):
    """Result table to register name column on it (via ZCML)."""

    sortOn = u'table-name-1'


class ExportForm(
        icemac.addressbook.browser.search.result.base.BaseSearchResultForm):
    """Export form showing a table containing names of the found persons."""

    table_class = PersonTable

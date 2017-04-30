import icemac.addressbook.browser.personlist
import icemac.addressbook.browser.search.result.base


class PersonTable(
        icemac.addressbook.browser.personlist.BasePersonList,
        icemac.addressbook.browser.search.result.base.BasePersonTable):
    """Result table displaying columns defined in user preferences."""

    values = (
        icemac.addressbook.browser.search.result.base.BasePersonTable.values)


class ExportForm(
        icemac.addressbook.browser.search.result.base.BaseSearchResultForm):
    """Export form showing a table of found results."""

    table_class = PersonTable

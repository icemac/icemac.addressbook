# -*- coding: utf-8 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.interfaces
import icemac.truncatetext
import z3c.table.column
import z3c.table.table


# Columns

class TitleLinkColumn(z3c.table.column.LinkColumn):
    """Column containing the title of an object and a link to the object."""

    header = _(u'Name')
    weight = 2

    def getSortKey(self, item):
        return icemac.addressbook.interfaces.ITitle(item).lower()

    def getLinkContent(self, item):
        return icemac.addressbook.interfaces.ITitle(item)


class DeleteLinkColumn(z3c.table.column.LinkColumn):
    """Column containing the a link to delete the object."""

    header = _(u'')
    weight = 100
    linkContent = _(u'Delete')
    linkName = '@@delete.html'


class TruncatedContentColumn(z3c.table.column.GetAttrColumn):

    length = 20
    attrName = None
    ellipsis = u'…'
    defaultValue = u''

    def getValue(self, obj):
        value = super(TruncatedContentColumn, self).getValue(obj)
        if value is None:
            return self.defaultValue
        result = icemac.truncatetext.truncate(value, self.length, self.ellipsis)
        return result


class KeywordsColumn(z3c.table.column.GetAttrColumn):
    """GetAttrColumn where attr is an iterable of keywords."""

    def getSortKey(self, item):
        return super(KeywordsColumn, self).getSortKey(item).lower()

    def getValue(self, obj):
        values = super(KeywordsColumn, self).getValue(obj)
        return u', '.join(sorted(
            (icemac.addressbook.interfaces.ITitle(x) for x in values),
            key=lambda x: x.lower()))



# Tables

class Table(z3c.table.table.Table):
    "Table which supports a no-rows-found message."

    cssClassEven = u'table-even-row'
    cssClassOdd = u'table-odd-row'
    startBatchingAt = 1000000
    no_rows_message = u'' # Set at subclass.

    def renderTable(self):
        if self.rows:
            return super(Table, self).renderTable()
        return self.no_rows_message


class PageletTable(z3c.pagelet.browser.BrowserPagelet, Table):
    """Render the table in a pagelet which also has a template.

    When no template is required the `Table` class can be used.
    """

    def __init__(self, *args, **kw):
        super(PageletTable, self).__init__(*args, **kw)
        Table.__init__(self, *args, **kw)
    update = Table.update

# -*- coding: utf-8 -*-
# Copyright (c) 2008-2014 Michael Howitz
# See also LICENSE.txt
from icemac.addressbook.i18n import _
import icemac.addressbook.interfaces
import icemac.truncatetext
import z3c.pagelet.browser
import z3c.table.batch
import z3c.table.column
import z3c.table.table
import zope.i18n


# Columns

class LinkColumn(icemac.addressbook.browser.base.BaseView,
                 z3c.table.column.LinkColumn):
    """LinkColumn which does not display a link when the URL is `None`.

    Also uses addressbook's URL computation method.

    """
    defaultValue = u''  # value which is rendered when there is no URL

    def getLinkURL(self, item):
        return self.url(item, self.linkName)

    def renderCell(self, item):
        if not self.getLinkURL(item):
            return self.defaultValue
        return super(LinkColumn, self).renderCell(item)


class TitleLinkColumn(LinkColumn):
    """Column containing the title of an object and a link to the object."""

    header = _(u'Name')
    weight = 2

    def getSortKey(self, item):
        return icemac.addressbook.interfaces.ITitle(item).lower()

    def getLinkContent(self, item):
        return icemac.addressbook.interfaces.ITitle(item)


class DeleteLinkColumn(LinkColumn):
    """Column containing the a link to delete the object."""

    header = _(u'')
    weight = 100
    linkContent = _(u'Delete')
    linkName = 'delete.html'


class TruncatedContentColumn(z3c.table.column.GetAttrColumn):
    "Column which truncates its content to `length` characters."

    length = 20  # number of characters to display
    attrName = None  # attribute to access
    ellipsis = u'…'  # ellipsis sign
    defaultValue = u''  # default value when there is no value

    def getValue(self, obj):
        value = super(TruncatedContentColumn, self).getValue(obj)
        if value is None:
            return self.defaultValue
        result = icemac.truncatetext.truncate(
            value, self.length, self.ellipsis)
        return result


class SourceColumn(z3c.table.column.GetAttrColumn):
    """GetAttrColumn where attr is a value or iterable out of a source."""

    attrName = NotImplemented
    soure = NotImplemented  # source the values are taken from

    def getSortKey(self, item):
        # Sort case insensitive:
        return super(SourceColumn, self).getSortKey(item).lower()

    def getValue(self, obj):
        values = super(SourceColumn, self).getValue(obj)
        if not hasattr(values, '__iter__'):
            if values is None:
                values = []
            else:
                values = [values]
        titles = [zope.i18n.translate(self.source.factory.getTitle(x),
                                      context=self.request)
                  for x in values]
        return u', '.join(sorted(titles, key=lambda x: x.lower()))


class KeywordsColumn(SourceColumn):
    """SourceColumn where attr is an iterable of keywords."""

    attrName = 'keywords'
    source = icemac.addressbook.interfaces.keyword_source


# Tables

class Table(z3c.table.table.Table):
    "Table which supports a no-rows-found message."

    cssClassEven = u'table-even-row'
    cssClassOdd = u'table-odd-row'
    startBatchingAt = 1000000
    no_rows_message = u''  # Set at subclass.

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


# Batching

class NiceBatchProvider(z3c.table.batch.BatchProvider):
    """A batch provider with a nicer spacer."""

    batchSpacer = u'…'

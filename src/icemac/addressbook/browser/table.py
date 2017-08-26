# -*- coding: utf-8 -*-
from icemac.addressbook.i18n import _
import datetime
import icemac.addressbook.browser.base
import icemac.addressbook.interfaces
import icemac.truncatetext
import z3c.pagelet.browser
import z3c.table.batch
import z3c.table.column
import z3c.table.table
import zope.i18n


END_OF_DATE = datetime.date(datetime.MAXYEAR, 12, 31)
END_OF_DATETIME = datetime.datetime(datetime.MAXYEAR, 12, 31, 23, 59, 59)


# Columns

class BaseColumn(z3c.table.column.Column):
    """Column knowing how to handle entities and fields in the address book.

    It adapts the `item`  to the defined entity and gets the value from the
    specified field.

    """

    # CAUTION: This column needs the following fields to be set:

    entity = NotImplemented  # referenced entity as object
    field = NotImplemented  # referenced field on entity as object
    defaultValue = u''  # Value for display when there is no value.

    def getRawValue(self, item):
        """Compute the value, which can be None."""
        schema_field = icemac.addressbook.entities.get_bound_schema_field(
            item, self.entity, self.field)
        # Returning the value of the bound object as it might differ from item:
        return schema_field.get(schema_field.context)

    def getValue(self, item):
        """Compute the value, mostly ready for display."""
        obj = self.getRawValue(item)
        if obj is None:
            return self.defaultValue
        return obj

    renderCell = getValue


class DateTimeColumn(z3c.table.column.FormatterColumn,
                     BaseColumn):
    """Column which is sortable even with `None` values in it."""

    maxValue = END_OF_DATETIME

    def renderCell(self, item):
        value = self.getRawValue(item)
        if value:
            return self.getFormatter().format(value)
        return self.defaultValue

    def getSortKey(self, item):
        # We use the isoformat as sort key, so comparison does not break if
        # we mix timezone naive and timezone aware datetimes. And yes, we
        # know that this might produce some glitches in the sort order but
        # it is better than an HTTP-500 and better than trying to guess
        # timezone information.
        key = self.getRawValue(item)
        if key is None:
            # empty date fields should be sorted to the end of the list
            key = self.maxValue
        return key.isoformat()


class DateColumn(DateTimeColumn):
    """DateColumn which is able to sort even `None` values."""

    formatterCategory = 'date'
    maxValue = END_OF_DATE


class LinkColumn(icemac.addressbook.browser.base.BaseView,
                 z3c.table.column.LinkColumn):
    """LinkColumn which uses address book's URL computation method."""

    def getLinkURL(self, item):
        return self.url(item, self.linkName)


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
    """Column which truncates its content to `length` characters."""

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
    """Table which supports a no-rows-found message."""

    title = None  # used by the breadrumbs
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

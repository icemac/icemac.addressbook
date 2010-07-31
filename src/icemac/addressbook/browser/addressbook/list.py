# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import _
import datetime
import icemac.addressbook.browser.table
import icemac.addressbook.interfaces
import z3c.table.column
import zope.component
import zope.i18n
import zope.preference.interfaces
import zope.schema.interfaces


END_OF_TIME = datetime.date(datetime.MAXYEAR,12,31)


class LinkColumn(z3c.table.column.LinkColumn):
    """LinkColumn which fetches link content from item."""

    attrName = None # Attribute wich contains the link content.
    defaultValue = u'' # value when attrName leads to a false value

    def getSortKey(self, item):
        # Sort by the value displayed to the user, but lowercase it,
        # as the user does not expect lower case names below the
        # 'normal' upper case ones.
        return self.getLinkContent(item).lower()

    def getLinkContent(self, item):
        # Get the content from item or return the default value when empty.
        return getattr(item, self.attrName) or self.defaultValue


class DateColumn(z3c.table.column.FormatterColumn,
                 z3c.table.column.GetAttrColumn):
    """Column which is sortable even with `None` values in it."""

    formatterCategory = 'date'

    def renderCell(self, item):
        value = self.getValue(item)
        if value is None:
            return self.defaultValue
        return self.getFormatter().format(value)

    def getSortKey(self, item):
        key = self.getValue(item)
        if key is None:
            # empty date fields should be sorted to the end of the list
            key = END_OF_TIME
        return key


class DoubleGetAttrColumn(z3c.table.column.GetAttrColumn):
    """Column which does two getattr calls in a row."""

    firstAttrName = None # name of the first attribute of the row
    attrName = None # name of the second attribute of the row

    def getValue(self, obj):
        "Compute the value in a row."
        return super(DoubleGetAttrColumn, self).getValue(
            getattr(obj, self.firstAttrName))

    def renderCell(self, obj):
        value = self.getValue(obj)
        if value is None:
            # Do not display `None` in the front end.
            return self.defaultValue
        return value


class TranslatedTiteledDoubleGetAttrColumn(DoubleGetAttrColumn):
    """DoubleGetAttrColumn which returns the translated ITitle of the value."""

    def getValue(self, obj):
        "Get the title of the value."
        value = super(TranslatedTiteledDoubleGetAttrColumn, self).getValue(obj)
        title = icemac.addressbook.interfaces.ITitle(value)
        translated = zope.i18n.translate(title, context=self.request)
        return translated


def getColumnClass(entity, field):
    """Get a column class to display the requested field of an entity."""
    if entity.interface == icemac.addressbook.interfaces.IPerson:
        if field.__name__ in ('first_name', 'last_name'):
            # First name and last name should be links ...
            return LinkColumn
        if field.__name__ == 'keywords':
            # Keywords need a special column as they are an iterable:
            return icemac.addressbook.browser.table.KeywordsColumn
        if (zope.schema.interfaces.IText.providedBy(field) and
            not zope.schema.interfaces.ITextLine.providedBy(field)):
            # The content of text areas (not text lines, which extend from
            # text area) should get truncated.
            return icemac.addressbook.browser.table.TruncatedContentColumn
        if zope.schema.interfaces.IDate.providedBy(field):
            # Date fields need a special column, as None values are not
            # compareable to date values:
            return DateColumn
    else:
        # address entities
        if field.__name__ == 'country':
            # country is an object, so the title of it should be displayed
            return TranslatedTiteledDoubleGetAttrColumn
        # all other address fields need the default column
        return DoubleGetAttrColumn


def getAdditionalColumnArgs(entity, field):
    """Get additional arguments to a specific column.

    Return a dict to be used as keyword args."""
    if entity.interface == icemac.addressbook.interfaces.IPerson:
        # Persons need no special arguments
        return {}
    else:
        # Addresses need the name of the default address attribute
        return dict(firstAttrName=entity.tagged_values.get('default_attrib'))


class PersonList(icemac.addressbook.browser.table.PageletTable):
    """List persons in address book."""

    no_rows_message = _(
        u'There are no persons entered yet, click on "Add person" to create '
        u'one.')

    @property
    def prefs(self):
        "User defined preferences for person list."
        return zope.component.getUtility(
            zope.preference.interfaces.IPreferenceGroup, name="personList")

    def __init__(self, *args, **kw):
        super(PersonList, self).__init__(*args, **kw)
        prefs = self.prefs
        order_by = prefs.order_by
        try:
            # Set the sort column to the value seleted in preferences.
            self.sortOn = '%s-%s-%s' % (
                self.prefix, order_by, prefs.columns.index(order_by))
        except ValueError:
            # When the order-by column is not displayed, use default
            # sort order.
            pass

    def setUpColumns(self):
        result = []
        for column_name in self.prefs.columns:
            entity, field = icemac.addressbook.preferences.sources.untokenize(
                column_name)
            column_class = getColumnClass(entity, field)
            result.append(
                z3c.table.column.addColumn(
                    self, column_class, column_name, attrName=field.__name__,
                    header=field.title, weight=len(result),
                    **getAdditionalColumnArgs(entity, field)))
        return result

    @property
    def values(self):
        return self.context.values()

# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import _
import datetime
import icemac.addressbook.browser.table
import icemac.addressbook.interfaces
import z3c.table.column
import zope.component
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


def getColumnClass(entity, field):
    """Get a column class to display the requested field of an entity."""
    if field.__name__ in ('first_name', 'last_name'):
        # First name and last name should be links ...
        return LinkColumn
    if field.__name__ == 'keywords':
        # Keywords need a special column as they are an iterable:
        return icemac.addressbook.browser.table.KeywordsColumn
    if zope.schema.interfaces.IDate.providedBy(field):
        # Date fields need a special column, as None values are not
        # compareable to date values:
        return DateColumn
    # All other fields are not special, so the default column is enough:
    return z3c.table.column.GetAttrColumn


class PersonList(icemac.addressbook.browser.table.PageletTable):
    """List persons in address book."""

    no_rows_message = _(
        u'There are no persons entered yet, click on "Add person" to create '
        u'one.')

    def setUpColumns(self):
        prefs = zope.component.getUtility(
            zope.preference.interfaces.IPreferenceGroup, name="personList")
        result = []
        for column_name in prefs.columns:
            entity, field = icemac.addressbook.preferences.sources.untokenize(
                column_name)
            column_class = getColumnClass(entity, field)
            result.append(
                z3c.table.column.addColumn(
                    self, column_class, column_name, attrName=field.__name__,
                header=field.title, weight=len(result)))
        return result

    @property
    def values(self):
        return self.context.values()

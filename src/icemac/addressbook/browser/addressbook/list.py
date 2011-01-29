# -*- coding: utf-8 -*-
# Copyright (c) 2009-2011 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import _
import datetime
import icemac.addressbook.browser.table
import icemac.addressbook.interfaces
import icemac.truncatetext
import z3c.form.term
import z3c.table.column
import zope.component
import zope.i18n
import zope.preference.interfaces
import zope.schema.interfaces


END_OF_DATE = datetime.date(datetime.MAXYEAR, 12, 31)
END_OF_DATETIME = datetime.datetime(datetime.MAXYEAR, 12, 31, 23, 59, 59)


class BaseColumn(z3c.table.column.Column):
    """Column which is able to get an object on an attribute of the item and
    adapt it to specified interface."""

    firstAttrName = None  # Name of the attribute to be selected first
    attrInterface = None  # Adapt to this interface
    attrName = None  # Get the attribute with this name as value
    defaultValue = u''  # Value for display when there is no value.

    def getObject(self, item):
        "Get the object for which has the attribute display."
        if self.firstAttrName:
            item = getattr(item, self.firstAttrName)
        if self.attrInterface:
            # Need to remove the security proxy here as otherwise the
            # user defined field data cannot be accessed (it is stored
            # in an annotation). This is no security hole, as the
            # value is only used for display.
            item = zope.security.proxy.getObject(item)
            item = self.attrInterface(item)
        return item

    def getRawValue(self, item):
        "Compute the value, which can be None."
        return getattr(self.getObject(item), self.attrName)

    def getValue(self, item):
        "Compute the value, mostly ready for display."
        obj = self.getRawValue(item)
        if obj is None:
            return self.defaultValue
        return obj

    renderCell = getValue


class LinkColumn(z3c.table.column.LinkColumn,
                 BaseColumn):
    """LinkColumn which fetches link content from item."""

    def getSortKey(self, item):
        # Sort by the value displayed to the user, but lowercase it,
        # as the user does not expect lower case names below the
        # 'normal' upper case ones.
        return self.getLinkContent(item).lower()

    def getLinkContent(self, item):
        # Get the content from item or return the default value when empty.
        return self.getValue(item)

    def renderCell(self, item):
        if self.getLinkContent(item):
            return super(LinkColumn, self).renderCell(item)
        return self.defaultValue


class URLColumn(LinkColumn):
    """LinkColumn where the link URL is the same as the link content."""

    getLinkURL = LinkColumn.getLinkContent


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
        key = self.getRawValue(item)
        if key is None:
            # empty date fields should be sorted to the end of the list
            key = self.maxValue
        return key


class DateColumn(DateTimeColumn):
    "DateColumn which is able to sort even `None` values."

    formatterCategory = 'date'
    maxValue = END_OF_DATE


class TruncatedContentColumn(BaseColumn):
    """Column which truncates its content."""

    length = 20  # number of characters to display
    ellipsis = u'…'  # ellipsis sign

    def renderCell(self, item):
        return icemac.truncatetext.truncate(
            self.getRawValue(item), self.length, self.ellipsis)


class BoolColumn(BaseColumn):
    "AdaptedGetAttrColumn for displaying bool values."

    def renderCell(self, item):
        value = self.getRawValue(item)
        # We use the labels of z3c.form here so the displayed values
        # are the same as in the edit form.
        if value is True:
            label = z3c.form.term.BoolTerms.trueLabel
        elif value is False:
            label = z3c.form.term.BoolTerms.falseLabel
        else:
            return self.defaultValue
        return zope.i18n.translate(label, context=self.request)


class TranslatedTiteledColumn(BaseColumn):
    """Column which returns the translated ITitle of the value."""

    def renderCell(self, obj):
        "Get the title of the value."
        value = self.getRawValue(obj)
        translated = self.defaultValue
        if value:
            title = icemac.addressbook.interfaces.ITitle(value)
            translated = zope.i18n.translate(title, context=self.request)
        return translated


class EMailColumn(BaseColumn,
                  z3c.table.column.EMailColumn):
    "Column which renders the cell contents as mailto-link."

    renderCell = z3c.table.column.EMailColumn.renderCell


def getColumnClass(entity, field):
    """Get a column class to display the requested field of an entity."""
    if field.__name__ in ('first_name', 'last_name'):
        # Person's first name and last name should be links:
        return LinkColumn
    if field.__name__ == 'keywords':
        # Keywords need a special column as they are an iterable:
        return icemac.addressbook.browser.table.KeywordsColumn
    if (zope.schema.interfaces.IText.providedBy(field) and
        not zope.schema.interfaces.ITextLine.providedBy(field)):
        # The content of text areas (but not text lines, which extend from
        # text area) should get truncated.
        return TruncatedContentColumn
    if zope.schema.interfaces.IDate.providedBy(field):
        # Date fields need a special column, as None values are not
        # compareable to date values:
        return DateColumn
    if field.__name__ == 'country':
        # Country is an object, so the translated title should be displayed:
        return TranslatedTiteledColumn
    if field.__name__ == 'email':
        # The e-mail address should be a mailto-link:
        return EMailColumn
    if field.__name__ == 'url':
        return URLColumn
    if icemac.addressbook.interfaces.IField.providedBy(field):
        # User defined fields:
        if field.type == u'Bool':
            return BoolColumn
        if field.type == u'URI':
            return URLColumn
        if field.type == u'Text':
            return TruncatedContentColumn
        if field.type == u'Date':
            return DateColumn
        if field.type == u'Datetime':
            return DateTimeColumn
    return BaseColumn


def getAdditionalColumnArgs(entity, field):
    """Get additional arguments to a specific column.

    Return a dict to be used as keyword args."""
    kw = dict()
    if icemac.addressbook.interfaces.IField.providedBy(field):
        # User defined fields need to be adapted
        kw['attrInterface'] = icemac.addressbook.interfaces.IUserFieldStorage
    if entity.interface != icemac.addressbook.interfaces.IPerson:
        # Addresses need the name of the default address attribute
        kw['firstAttrName'] = entity.tagged_values.get('default_attrib')
    if (field.__name__ == 'url' or
        (icemac.addressbook.interfaces.IField.providedBy(field) and
         field.type == 'URI')):
        kw['linkTarget'] = '_blank'
    return kw


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
        self.sortOrder = self.prefs.sort_direction
        self.startBatchingAt = self.prefs.batch_size
        self.batchSize = self.prefs.batch_size
        self._columns = self._set_up_columns_and_sort_on()

    def _set_up_columns_and_sort_on(self):
        "Creates the columns and compute the order-by column."
        prefs = self.prefs
        order_by = prefs.order_by
        columns = []
        index = 0  # current column index
        # Entity and field of the column which sould be used for order-by:
        try:
            order_by_entity, order_by_field = (
                icemac.addressbook.preferences.sources.untokenize(
                    order_by))
        except KeyError:
            # Field has been deleted, so we can't use it for sorting:
            order_by_entity, order_by_field = None, None

        # Create all columns and compute the order-by column:
        for column_name in self.prefs.columns:
            try:
                entity, field = (
                    icemac.addressbook.preferences.sources.untokenize(
                        column_name))
            except KeyError:
                # Column no longer exists
                continue
            columns.append(
                z3c.table.column.addColumn(
                    self, getColumnClass(entity, field), field.__name__,
                    attrName=field.__name__, header=field.title,
                    weight=index, **getAdditionalColumnArgs(entity, field)
                    ))
            if entity == order_by_entity and field == order_by_field:
                # Found the entity and field for order by, so set the
                # expected name on the sortOn variable:
                self.sortOn = '%s-%s-%s' % (self.prefix, field.__name__, index)
            # current column exists, so the index can be adjusted
            index += 1
        return columns

    def setUpColumns(self):
        "Return the previously computed columns."
        return self._columns

    @property
    def values(self):
        "The values are stored on the context."
        return self.context.values()

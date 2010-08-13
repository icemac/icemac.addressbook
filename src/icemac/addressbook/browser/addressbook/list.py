# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
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


END_OF_TIME = datetime.date(datetime.MAXYEAR,12,31)


class BaseColumn(z3c.table.column.Column):
    """Column which is able to get an object on an attribute of the item and
    adapt it to specified interface."""

    firstAttrName = None # Name of the attribute to be selected first
    attrInterface = None # Adapt to this interface
    attrName = None # Get the attribute with this name as value
    defaultValue = u'' # Value for display when there is no value.

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


class DateColumn(z3c.table.column.FormatterColumn,
                 BaseColumn):
    """Column which is sortable even with `None` values in it."""

    formatterCategory = 'date'

    def renderCell(self, item):
        value = self.getRawValue(item)
        if value:
            return self.getFormatter().format(value)
        return self.defaultValue

    def getSortKey(self, item):
        key = self.getRawValue(item)
        if key is None:
            # empty date fields should be sorted to the end of the list
            key = END_OF_TIME
        return key


class TruncatedContentColumn(BaseColumn):
    """Column which truncates its content."""

    length = 20 # number of characters to display
    ellipsis = u'…' # ellipsis sign

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
            return z3c.form.term.BoolTerms.trueLabel
        if value is False:
            return z3c.form.term.BoolTerms.falseLabel
        return self.defaultValue


class TranslatedTiteledColumn(BaseColumn):
    """Column which returns the translated ITitle of the value."""

    def renderCell(self, obj):
        "Get the title of the value."
        value = self.getRawValue(obj)
        if value:
            title = icemac.addressbook.interfaces.ITitle(value)
            translated = zope.i18n.translate(title, context=self.request)
        else:
            translated = self.defaultValue
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
        prefs = self.prefs
        order_by = prefs.order_by
        entity, field = icemac.addressbook.preferences.sources.untokenize(
            order_by)
        field_name = field.__name__
        try:
            # Set the sort column to the value seleted in preferences.
            self.sortOn = '%s-%s-%s' % (
                self.prefix, field_name, prefs.columns.index(order_by))
        except ValueError:
            # When the order-by column is not displayed, use default
            # sort order.
            pass
        self.sortOrder = prefs.sort_direction

    def setUpColumns(self):
        result = []
        for column_name in self.prefs.columns:
            entity, field = icemac.addressbook.preferences.sources.untokenize(
                column_name)
            column_class = getColumnClass(entity, field)
            result.append(
                z3c.table.column.addColumn(
                    self, column_class, field.__name__, attrName=field.__name__,
                    header=field.title, weight=len(result),
                    **getAdditionalColumnArgs(entity, field)))
        return result

    @property
    def values(self):
        return self.context.values()

# -*- coding: utf-8 -*-
import icemac.addressbook.browser.table
import icemac.addressbook.fieldsource
import icemac.addressbook.interfaces
import icemac.truncatetext
import z3c.form.term
import z3c.table.column
import zope.component
import zope.i18n
import zope.preference.interfaces
import zope.schema.interfaces


class LinkColumn(z3c.table.column.LinkColumn,
                 icemac.addressbook.browser.table.BaseColumn):
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


class TruncatedContentColumn(icemac.addressbook.browser.table.BaseColumn):
    """Column which truncates its content."""

    length = 20  # number of characters to display
    ellipsis = u'…'  # ellipsis sign

    def renderCell(self, item):
        return icemac.truncatetext.truncate(
            self.getRawValue(item), self.length, self.ellipsis)


class BoolColumn(icemac.addressbook.browser.table.BaseColumn):
    """AdaptedGetAttrColumn for displaying bool values."""

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


class TranslatedTiteledColumn(icemac.addressbook.browser.table.BaseColumn):
    """Column which returns the translated ITitle of the value."""

    def renderCell(self, obj):
        """Get the title of the value."""
        value = self.getRawValue(obj)
        translated = self.defaultValue
        if value:
            title = icemac.addressbook.interfaces.ITitle(value)
            translated = zope.i18n.translate(title, context=self.request)
        return translated


class EMailColumn(icemac.addressbook.browser.table.BaseColumn,
                  z3c.table.column.EMailColumn):
    """Column which renders the cell contents as mailto-link."""

    renderCell = z3c.table.column.EMailColumn.renderCell


USER_DEFINED_FIELD_TYPE__TO__COLUMN = {
    u'Bool': BoolColumn,
    u'URI': URLColumn,
    u'Text': TruncatedContentColumn,
    u'Date': icemac.addressbook.browser.table.DateColumn,
    u'Datetime': icemac.addressbook.browser.table.DateTimeColumn,
}


FIELD_NAME__TO__COLUMN = {
    'first_name': LinkColumn,
    'last_name': LinkColumn,
    'keywords': icemac.addressbook.browser.table.KeywordsColumn,
    'country': TranslatedTiteledColumn,
    'email': EMailColumn,
    'url': URLColumn,
}


def getColumnClass(entity, field):
    """Get a column class to display the requested field of an entity."""
    column_class = FIELD_NAME__TO__COLUMN.get(field.__name__, None)
    if column_class is not None:
        return column_class
    if (zope.schema.interfaces.IText.providedBy(field) and
            not zope.schema.interfaces.ITextLine.providedBy(field)):
        # The content of text areas (but not text lines, which extend from
        # text area) should get truncated.
        return TruncatedContentColumn
    if zope.schema.interfaces.IDate.providedBy(field):
        # Date fields need a special column, as None values are not
        # compareable to date values:
        return icemac.addressbook.browser.table.DateColumn
    if icemac.addressbook.interfaces.IField.providedBy(field):
        return USER_DEFINED_FIELD_TYPE__TO__COLUMN.get(
            field.type, icemac.addressbook.browser.table.BaseColumn)
    # Field is e. g. a TextLine
    return icemac.addressbook.browser.table.BaseColumn


def createFieldColumn(table, entity, field, weight):
    """Create a column for the specified `entity` and `field`."""
    additional_column_args = dict()
    if (field.__name__ == 'url' or
        (icemac.addressbook.interfaces.IField.providedBy(field) and
         field.type == 'URI')):
        additional_column_args['linkTarget'] = '_blank'
    title = icemac.addressbook.entities.get_field_label(field)

    return z3c.table.column.addColumn(
        table, getColumnClass(entity, field), field.__name__,
        header=title, weight=weight,
        entity=entity, field=field, **additional_column_args)


class BasePersonList(object):
    """List persons in address book without batching.

    Either extend `icemac.addressbook.browser.table.PageletTable`
    or `icemac.addressbook.browser.table.Table`.
    """

    def __init__(self, context, request, prefs=None):
        super(BasePersonList, self).__init__(context, request)
        self.sortOrder = self.prefs.personLists.sort_direction

    @property
    def prefs(self):
        """User defined preferences for person list."""
        return zope.component.getUtility(
            zope.preference.interfaces.IPreferenceGroup, name="ab")

    def update(self):
        self._columns = self._set_up_columns()
        super(BasePersonList, self).update()

    def _set_up_columns(self):
        """Create the columns of the table."""
        zcml_columns = super(BasePersonList, self).setUpColumns()
        zcml_columns_before = len(
            [x for x in zcml_columns if z3c.table.table.getWeight(x) < 0])
        python_columns = self._set_up_user_selected_columns_and_sort_on(
            zcml_columns_before)
        return zcml_columns + python_columns

    def _set_up_user_selected_columns_and_sort_on(self, columns_before):
        """Create the columns selected by the user in the preferences.

        Additionally computes the sort order.
        """
        order_by = self.prefs.personLists.order_by
        columns = []
        index = 0  # current column index
        # Entity and field of the column which should be used for order-by:
        try:
            order_by_entity, order_by_field = (
                icemac.addressbook.fieldsource.untokenize(order_by))
        except KeyError:
            # Field has been deleted, so we can't use it for sorting:
            order_by_entity, order_by_field = None, None

        # Create all columns and compute the order-by column:
        for column_name in self.prefs.personLists.columns:
            try:
                entity, field = (
                    icemac.addressbook.fieldsource.untokenize(column_name))
            except KeyError:
                # Column no longer exists
                continue
            columns.append(createFieldColumn(self, entity, field, index))
            if entity == order_by_entity and field == order_by_field:
                # Found the entity and field for order by, so set the
                # expected name on the sortOn variable. The last parameter
                # depends on the position of the column in the table when
                # there are columns before the columns defined by this
                # method the index gets higher:
                self.sortOn = '%s-%s-%s' % (
                    self.prefix, field.__name__, index + columns_before)
            # current column exists, so the index can be adjusted
            index += 1
        return columns

    def setUpColumns(self):
        """Return the computed columns and via ZCML registered ones."""
        return self._columns

    values = NotImplemented

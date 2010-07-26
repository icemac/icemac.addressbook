# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import _
import icemac.addressbook.browser.table
import icemac.addressbook.interfaces
import z3c.table.column


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


class PersonList(icemac.addressbook.browser.table.PageletTable):
    """List persons in address book."""

    no_rows_message = _(
        u'There are no persons entered yet, click on "Add person" to create '
        u'one.')

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, LinkColumn, 'lastname', attrName='last_name',
                header=_(u'last name'), weight=1),
            z3c.table.column.addColumn(
                self, LinkColumn, 'firstname', attrName='first_name',
                header=_(u'first name'), weight=1),
            ]

    @property
    def values(self):
        return self.context.values()

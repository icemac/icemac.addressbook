# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.browser.table
import icemac.addressbook.importer.readers.base
import z3c.form.button
import z3c.form.field
import z3c.formui.form
import z3c.pagelet.browser
import zope.interface
import zope.schema


class Overview(z3c.pagelet.browser.BrowserPagelet,
               icemac.addressbook.browser.table.Table):

    no_rows_message = _(
        u'No import files uploaded, yet.')

    update = icemac.addressbook.browser.table.Table.update

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, icemac.addressbook.browser.table.TitleLinkColumn,
                'file', weight=1),
            z3c.table.column.addColumn(
                self, z3c.table.column.GetAttrColumn, 'mimeType', weight=2,
                header=_(u'MIME type'), attrName='mimeType'),
            z3c.table.column.addColumn(
                self, icemac.addressbook.browser.table.TruncatedContentColumn,
                'notes', weight=3,
                header=_(u'Notes'), attrName='notes', length=50),
#             z3c.table.column.addColumn(
#                 self, z3c.table.column.CreatedColumn,
#                 'created', weight=4),
#             z3c.table.column.addColumn(
#                 self, z3c.table.column.ModifiedColumn,
#                 'created', weight=5),
            z3c.table.column.addColumn(
                self, icemac.addressbook.browser.table.DeleteLinkColumn,
                'delete', weigth=6),
            z3c.table.column.addColumn(
                self, z3c.table.column.LinkColumn, 'import', weight=200,
                header=_(u''), linkContent=_(u'Import'),
                linkName='@@import.html'),
            ]

    @property
    def values(self):
        return self.context.values()


class IReadersList(zope.interface.Interface):
    "A list of import readers which are able to read the file."

    reader = zope.schema.Choice(
        title=_(u'Import file reader'),
        source=icemac.addressbook.importer.readers.base.Source())


class ChooseReader(z3c.formui.form.Form):

    ignoreContext = True
    fields = z3c.form.field.Fields(IReadersList)

    @z3c.form.button.buttonAndHandler(_('Import'), name='import')
    def handleImport(self, action):
        pass

    @z3c.form.button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        pass

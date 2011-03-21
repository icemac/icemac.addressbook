# -*- coding: utf-8 -*-
# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.browser.base
import icemac.addressbook.export.sources
import icemac.addressbook.interfaces
import z3c.form.button
import z3c.ptcompat
import z3c.table.column
import zc.sourcefactory.interfaces
import zope.interface
import zope.schema
import zope.session.interfaces


class IExporterChoice(zope.interface.Interface):

    exporter = zope.schema.Choice(
        title=_(u'Export using'),
        source=icemac.addressbook.export.sources.exporter_source)


class BaseExportForm(icemac.addressbook.browser.base.BaseEditForm):
    """Base form for exports allowing multiple export formats."""

    ignoreContext = True
    interface = IExporterChoice
    template = z3c.ptcompat.ViewPageTemplateFile('export.pt')
    id = 'search-export-form'
    table_class = NotImplemented

    def renderTable(self):
        table = self.table_class(self.__parent__, self.request)
        table.update()
        return table.render()

    def _store_data_in_session(self):
        """Store data in session and return `True` on success."""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return False
        session = zope.session.interfaces.ISession(self.request)[
            icemac.addressbook.interfaces.PACKAGE_ID]
        session['person_ids'] = self.request.form.get('persons', ())
        session['exporter_token'] = zc.sourcefactory.interfaces.IToken(
            data['exporter'])
        return True

    @z3c.form.button.buttonAndHandler(_('Export'), name='export')
    def handleExport(self, action):
        if self._store_data_in_session():
            self.request.response.redirect('@@export.html')

    @z3c.form.button.buttonAndHandler(
        _('Delete selected persons'), name='delete',
        condition=icemac.addressbook.browser.base.can_access(
            '@@delete_persons.html'))
    def handleDelete(self, action):
        if self._store_data_in_session():
            self.request.response.redirect('@@delete_persons.html')


class BasePersonTable(icemac.addressbook.browser.table.Table):
    "Base result table displaying at least a checkbox column (using ZCML)."

    def update(self):
        self.result = self.context.result
        if self.result is not None:
            # only render table when a search happend
            super(BasePersonTable, self).update()

    @property
    def values(self):
        return self.result


class CheckBoxColumn(z3c.table.column.CheckBoxColumn):
    """Table column to show checkboxes to select result rows for export."""

    header = u''
    weight = -1

    def getItemKey(self, item):
        return 'persons:list'

    def isSelected(self, item):
        if self.request.get(self.getItemKey(item), None) is None:
            # not in request, return default: selected
            return True
        return super(CheckBoxColumn, self).isSelected(item)

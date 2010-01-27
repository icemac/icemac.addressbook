# -*- coding: utf-8 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.browser.base
import icemac.addressbook.export.sources
import icemac.addressbook.interfaces
import z3c.form.button
import z3c.ptcompat
import z3c.table.column
import z3c.table.table
import zc.sourcefactory.interfaces
import zope.interface
import zope.schema
import zope.session.interfaces


class IExporterChoice(zope.interface.Interface):

    exporter = zope.schema.Choice(
        title=_(u'Export using'),
        source=icemac.addressbook.export.sources.exporter_source)


class ExportForm(icemac.addressbook.browser.base.BaseEditForm):

    ignoreContext = True
    interface = IExporterChoice
    template = z3c.ptcompat.ViewPageTemplateFile('export.pt')

    def renderTable(self):
        table = PersonTable(self.__parent__, self.request)
        table.update()
        return table.render()

    @z3c.form.button.buttonAndHandler(_('Export'), name='export')
    def handleExport(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        session = zope.session.interfaces.ISession(self.request)[
            icemac.addressbook.interfaces.PACKAGE_ID]
        session['person_ids'] = self.request.form.get('persons', ())
        session['exporter_token'] = zc.sourcefactory.interfaces.IToken(
            data['exporter'])
        self.request.response.redirect('@@export.html')


class PersonTable(icemac.addressbook.browser.table.Table):
    "Person table viewlet."

    sortOn = u'table-name-1'

    def update(self):
        self.result = self.context.result
        if self.result is not None:
            # only render table when a search happend
            super(PersonTable, self).update()

    @property
    def values(self):
        return self.result


class CheckBoxColumn(z3c.table.column.CheckBoxColumn):

    header = u''
    weight = 1

    def getItemKey(self, item):
        return 'persons:list'

    def isSelected(self, item):
        if self.request.get(self.getItemKey(item), None) is None:
            # not in request, return default: selected
            return True
        return super(CheckBoxColumn, self).isSelected(item)

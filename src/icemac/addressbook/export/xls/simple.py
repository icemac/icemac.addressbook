# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import cStringIO
import datetime
import decimal
import icemac.addressbook.address
import icemac.addressbook.export.base
import icemac.addressbook.export.interfaces
import icemac.addressbook.interfaces
import xlwt
import zope.component
import zope.i18n
import zope.i18nmessageid
import zope.interface
import zope.publisher.interfaces.browser
import zope.security.proxy


# fonts
head_font = xlwt.Font()
head_font.name = 'Courier'

group_font = xlwt.Font()
group_font.name = 'Courier'
group_font.bold = True


# styles
default_style = xlwt.XFStyle()

head_style = xlwt.XFStyle()
head_style.font = head_font

group_style = xlwt.XFStyle()
group_style.font = group_font

date_style = xlwt.XFStyle()
date_style.num_format_str = 'DD.MM.YY'

datetime_style = xlwt.XFStyle()
datetime_style.num_format_str = 'DD.MM.YY HH:MM:SS'

value_style_mapping = {
    datetime.date: date_style,
    datetime.datetime: datetime_style,
    }


class XLSExport(icemac.addressbook.export.base.BaseExporter):
    """Abstract base class for xls export."""

    file_extension = 'xls'
    mime_type = 'application/vnd.ms-excel'

    def getEntity(self, interface):
        return zope.component.getUtility(
            icemac.addressbook.interfaces.IEntities).getEntity(interface)

    def convert_value(self, value):
        """Convert the value for xls export."""
        if value is None:
            return value
        if value.__class__ in (str, unicode, float, int, bool, datetime.date,
                               datetime.datetime, decimal.Decimal):
            return self.translate(value)
        if hasattr(value, '__iter__'):
            return ', '.join(self.convert_value(v) for v in value)
        return self.translate(icemac.addressbook.interfaces.ITitle(value))

    def translate(self, value):
        if not isinstance(value, zope.i18nmessageid.Message):
            return value
        return zope.i18n.translate(value, context=self.request)

    def export(self):
        self.workbook = xlwt.Workbook()
        self.sheet = self.workbook.add_sheet(
            self.translate(_(u'Address book - Export')))
        self.col = 0

        self._export()

        io = cStringIO.StringIO()
        self.workbook.save(io)
        return io.getvalue()

    def write_headlines(self, col, interface, headline):
        self.sheet.write(0, col, headline, group_style)
        for field in self.getEntity(interface).getFieldValuesInOrder():
            self.sheet.write(1, col, self.translate(field.title), head_style)
            col += 1
        return col

    def write_cell(self, row, col, value):
        style = value_style_mapping.get(value.__class__, default_style)
        self.sheet.write(row, col, self.convert_value(value), style)

    def write_col(self, interface, obj_getter, headline):
        max_col = self.write_headlines(self.col, interface, headline)
        row = 1
        for person in self.persons:
            row += 1
            obj = obj_getter(person)
            self.write_obj(row, self.col, interface, obj)
        self.col = max_col

    def write_obj(self, row, col, interface, obj):
        if obj is None:
            return col
        idx = 0
        for name, field in self.getEntity(interface).getFieldsInOrder():
            # Need to remove the security proxy to access the user
            # defined fields.
            context = field.interface(zope.security.proxy.getObject(obj))
            self.write_cell(row, col + idx, getattr(context, name))
            idx += 1
        return col + idx

    def write_person_data(self):
        self.write_col(
            icemac.addressbook.interfaces.IPerson,
            lambda x:x,
            self.translate(_('person')))


class DefaultsExport(XLSExport):

    title = _(u'XLS main')
    description = _(
        u'Exports person data and main addresses resp. phone numbers.')

    def _export(self):
        self.write_person_data()
        for address in icemac.addressbook.address.address_mapping:
            self.write_col(address['interface'],
                           lambda x:getattr(x, 'default_'+address['prefix']),
                           self.translate(address['title']))


class CompleteExport(XLSExport):

    title = _(u'XLS complete')
    description = _(
        u'Exports person data and all addresses resp. phone numbers.')

    def _export(self):
        self.write_person_data()
        for address in icemac.addressbook.address.address_mapping:
            self.write_block(
                address['interface'], address['prefix'], address['title'])

    def write_block(self, iface, prefix, title):
        num_blocks = 0
        blocks_with_header = 0
        start_col = max_col = self.col
        row = 1
        for person in self.persons:
            row += 1
            # write default objs first
            default_obj = getattr(person, 'default_' + prefix)
            if default_obj is None:
                continue
            if num_blocks == 0:
                max_col = self.write_headlines(
                    start_col, iface,
                    self.translate(
                        _(u'${prefix} ${title}',
                          mapping=dict(prefix=_(u'main'), title=title))))
                num_blocks = 1
                blocks_with_header = 1
            col = self.write_obj(row, start_col, iface, default_obj)
            if col == start_col:
                # nothing written because there was no obj
                continue
            # write other objs after default obj
            objs = [obj
                    for obj in icemac.addressbook.utils.iter_by_interface(
                        person, iface)
                    if obj != default_obj]
            if not objs:
                continue
            num_blocks = max(num_blocks, len(objs) + 1)
            while blocks_with_header < num_blocks:
                max_col = self.write_headlines(
                    max_col, iface,
                    self.translate(
                        _(u'${prefix} ${title}',
                          mapping=dict(prefix=_(u'other'), title=title)))
                    )
                blocks_with_header += 1
            for obj in objs:
                col = self.write_obj(row, col, iface, obj)
        self.col = max_col

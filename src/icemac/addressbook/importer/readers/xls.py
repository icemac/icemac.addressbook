# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import MessageFactory as _
import datetime
import icemac.addressbook.importer.interfaces
import icemac.addressbook.importer.readers.base
import mmap
import xlrd
import zope.interface


class XLSReader(icemac.addressbook.importer.readers.base.BaseReader):
    """Import reader for XLS files."""

    title = _(u'Microsoft Excel file')
    contents = None

    @classmethod
    def open(cls, file_handle):
        reader = super(XLSReader, cls).open(file_handle)
        reader.contents = mmap.mmap(
            reader.file.fileno(), 0, access=mmap.ACCESS_READ)
        reader.wb = xlrd.open_workbook(file_contents=reader.contents)
        reader.sheet = reader.wb.sheet_by_index(0)
        reader.field_names = reader.sheet.row_values(0)
        return reader

    def __del__(self):
        if self.contents is not None:
            self.contents.close()
        super(XLSReader, self).__del__()

    def _convert_value(self, value):
        res = value.value
        if value.ctype == xlrd.XL_CELL_DATE:
            date_tuple = xlrd.xldate_as_tuple(res, self.wb.datemode)
            res = datetime.date(*date_tuple[:3])
        elif res == '':
            res = None
        return res

    def getFieldNames(self):
        """Get the names of the fields in the file."""
        return self.field_names

    def getFieldSamples(self, field_name):
        """Get sample values for a field."""
        for val in self.sheet.col_slice(self.field_names.index(field_name),
                                        1, 4):
            val = self._convert_value(val)
            if val is None:
                val = u''
            elif isinstance(val, datetime.date):
                val = unicode(val.strftime('%Y-%m-%d'))
            yield val

    def __iter__(self):
        """Iterate over the file."""
        for index in xrange(1, self.sheet.nrows):
            keys = [field_idx
                    for field_idx, name in enumerate(self.field_names)]
            values = [self._convert_value(val) for val in self.sheet.row(index)]
            yield dict(zip(keys, values))

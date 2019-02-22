from icemac.addressbook.i18n import _
from io import BytesIO
import datetime
import decimal
import icemac.addressbook.export.base
import icemac.addressbook.interfaces
import icemac.addressbook.utils
import six
import xlwt
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
    base_types = six.string_types + (
        float, int, bool, datetime.date, datetime.datetime, decimal.Decimal)

    def convert_value(self, value):
        """Convert the value for xls export."""
        if value is None:
            return value
        if isinstance(value, self.base_types):
            return self.translate(value)
        if hasattr(value, '__iter__'):
            return ', '.join(self.convert_value(v) for v in value)
        return self.translate(icemac.addressbook.interfaces.ITitle(value))

    def translate(self, value):
        return icemac.addressbook.utils.translate(value, self.request)

    def export(self):
        self.workbook = xlwt.Workbook()
        self.sheet = self.workbook.add_sheet(
            self.translate(_(u'Address book - Export')))
        self.col = 0

        self._export()

        io = BytesIO()
        self.workbook.save(io)
        return io.getvalue()

    def write_headlines(self, col, interface, headline):
        self.sheet.write(0, col, headline, group_style)
        fields = icemac.addressbook.interfaces.IEntity(
            interface).getFieldValues()

        address_book = icemac.addressbook.interfaces.IAddressBook(None)
        customization = icemac.addressbook.interfaces.IFieldCustomization(
            address_book)
        for field in fields:
            title = customization.query_value(field, u'label')
            self.sheet.write(1, col, self.translate(title), head_style)
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
        idx = 0
        names_fields = icemac.addressbook.interfaces.IEntity(
            interface).getFields()
        for name, field in names_fields:
            # Need to remove the security proxy to access the user
            # defined fields.
            context = field.interface(zope.security.proxy.getObject(obj))
            self.write_cell(row, col + idx, getattr(context, name))
            idx += 1
        return col + idx

    def write_person_data(self):
        self.write_col(
            icemac.addressbook.interfaces.IPerson,
            lambda x: x,
            self.translate(_('person')))

    def get_entities(self):
        return zope.component.getUtility(
            icemac.addressbook.interfaces.IEntities).getMainEntities()


class DefaultsExport(XLSExport):
    """Exports person data and main addresses resp. phone numbers."""

    def _export(self):
        for entity in self.get_entities():
            if entity.interface == icemac.addressbook.interfaces.IPerson:
                self.write_person_data()
            else:
                self.write_col(
                    entity.interface,
                    lambda x: getattr(
                        x, entity.tagged_values['default_attrib']),
                    self.translate(entity.title))


class CompleteExport(XLSExport):
    """Exports person data and all addresses resp. phone numbers."""

    def _export(self):
        for entity in self.get_entities():
            if entity.interface == icemac.addressbook.interfaces.IPerson:
                self.write_person_data()
            else:
                self.write_block(
                    entity.interface, entity.tagged_values['default_attrib'],
                    entity.title)

    def write_block(self, iface, default_attrib, title):
        num_blocks = 0
        blocks_with_header = 0
        start_col = max_col = self.col
        row = 1
        for person in self.persons:
            row += 1
            # write default objs first
            default_obj = getattr(person, default_attrib)
            if default_obj is None:
                continue
            if num_blocks == 0:
                max_col = self.write_headlines(
                    start_col, iface,
                    self.translate(
                        _(u'main ${address}', mapping=dict(address=title))))
                num_blocks = 1
                blocks_with_header = 1
            col = self.write_obj(row, start_col, iface, default_obj)
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
                        _(u'other ${address}', mapping=dict(address=title)))
                )
                blocks_with_header += 1
            for obj in objs:
                col = self.write_obj(row, col, iface, obj)
        self.col = max_col

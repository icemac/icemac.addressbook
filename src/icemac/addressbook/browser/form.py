# -*- coding: utf-8 -*-
from js.jquery_timepicker_addon import timepicker_locales, timepicker
from js.jqueryui import base as jqueryui_css
from js.jqueryui import ui_datepicker_locales, ui_selectable
import grokcore.component as grok
import icemac.addressbook.browser.interfaces
import icemac.addressbook.interfaces
import icemac.addressbook.preferences.utils
import json
import pytz
import z3c.form.browser.select
import z3c.form.browser.text
import z3c.form.converter
import z3c.form.hint
import z3c.form.interfaces
import z3c.form.widget
import zope.interface
import zope.schema.interfaces


class DatetimeDataConverter(z3c.form.converter.DatetimeDataConverter):
    """Converter for z3c.form displaying localized date times.

    Converts stored datetimes to timezone of request.
    Converts datetimes from form to store with time zone of request.

    """

    @property
    def time_zone(self):
        """User selected time zone."""
        return icemac.addressbook.preferences.utils.get_time_zone()

    def toWidgetValue(self, value):
        """Convert to time zone user has selected."""
        if value is not self.field.missing_value and value.tzinfo is not None:
            value = value.astimezone(self.time_zone)
        return super(DatetimeDataConverter, self).toWidgetValue(value)

    def toFieldValue(self, value):
        value = super(DatetimeDataConverter, self).toFieldValue(value)
        if value is None:
            return value
        return self.time_zone.localize(value).astimezone(pytz.UTC)


# Map zope.i18n binary pattern to jquery pattern:
# Sources:
# * http://api.jqueryui.com/datepicker
# * http://trentrichardson.com/examples/timepicker/#tp-formatting
# * https://github.com/zopefoundation/zope.i18n/blob/
#           b8fff2676a7575bf2d3248c562f778776e0603ce/src/zope/i18n/interfaces/
#           __init__.py#L377
pattern_mapping = {
    'date': {
        ('y', 2): 'y',
        ('y', 4): 'yy',
        ('M', 1): 'm',
        ('M', 2): 'mm',
        ('M', 3): 'M',
        ('M', 4): 'MM',
        ('D', 1): 'o',
        ('D', 2): 'o',
        ('D', 3): 'oo',
        ('E', 3): 'D',
        ('E', 4): 'DD',
    },
    'time': {
        ('H', 1): 'h',
        ('H', 2): 'HH',
        ('h', 1): 'h',
        ('S', 1): 'l',
        ('a', 1): 'TT',
        ('a', 2): 'TT',
    }
}
pattern_mapping['datetime'] = pattern_mapping['date'].copy()
pattern_mapping['datetime'].update(pattern_mapping['time'])
# Mappings of jquery and zope.i18n do not exactly match:
pattern_mapping['datetime'][('h', 1)] = 'hh'


def zope_i18n_pattern_to_jquery_pattern(kind, pattern):
    """Convert a zope.i18n datetime pattern to one of jquery."""
    # bin_pattern is a list of tuples (char, count) or chars
    bin_pattern = zope.i18n.format.parseDateTimePattern(pattern)
    # pattern_mapping contains only the differences, so by default produce
    # char * count (or the char if it is no tuple):
    pattern = ''.join(
        [pattern_mapping[kind].get(
            x, x[0] * x[1] if isinstance(x, tuple) else x)
         for x in bin_pattern])
    return pattern


class DatetimeWidgetBase(z3c.form.browser.text.TextWidget):
    """Base class widget to enter date and time using JavaScript picker."""

    klass = NotImplemented
    picker_js_func_name = NotImplemented
    type = NotImplemented

    def get_parameters(self):
        converter = z3c.form.interfaces.IDataConverter(self)
        params = {}
        if 'date' in self.picker_js_func_name:
            params.update(
                {'dateFormat': self.get_format(converter, 'date', self.type),
                 'changeMonth': True,
                 'changeYear': True,
                 'yearRange': '-100:+10',
                 'firstDay': 0,
                 'numberOfMonths': 3,
                 'stepMonths': 3})
        if 'time' in self.picker_js_func_name:
            params.update(
                {'timeFormat': self.get_format(converter, 'time', self.type),
                 'hourGrid': 4,
                 'hourMin': 6,
                 'hourMax': 22,
                 'minuteGrid': 15,
                 'stepMinute': 15})
        return params

    def get_format(self, converter, type, for_):
        """Get the jQuery format string from a z3c.form converter.

        converter ... z3c.form data converter instance
        type ... 'date' or 'time'
        for_ ... 'date', 'time', or 'datetime'

        """
        getFormatter = self.request.locale.dates.getFormatter
        return zope_i18n_pattern_to_jquery_pattern(
            for_, getFormatter(type, converter.length).getPattern())

    def update(self):
        super(DatetimeWidgetBase, self).update()
        locale_name = self.request.locale.id.language
        jqueryui_css.need()
        timepicker.need()
        if locale_name in timepicker_locales:
            timepicker_locales[locale_name].need()
        if locale_name in ui_datepicker_locales:
            ui_datepicker_locales[locale_name].need()

    def javascript(self):
        return "jQuery('#%s').%s(%s);" % (
            self.id, self.picker_js_func_name,
            json.dumps(self.get_parameters()))


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IDatetimeWidget)
class DatetimeWidget(DatetimeWidgetBase):
    """Widget to enter date and time using JavaScript picker."""

    klass = 'datetime-widget'
    picker_js_func_name = 'datetimepicker'
    type = 'datetime'


@grok.adapter(
    zope.schema.interfaces.IDatetime,
    icemac.addressbook.browser.interfaces.IAddressBookLayer)
@grok.implementer(z3c.form.interfaces.IFieldWidget)
def DatetimeFieldWidget(field, request):
    """Factory for DatetimeWidget."""
    return z3c.form.widget.FieldWidget(field, DatetimeWidget(request))


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IDateWidget)
class DateWidget(DatetimeWidgetBase):
    """Widget to enter date using a JavaScript picker."""

    klass = 'date-widget'
    picker_js_func_name = 'datepicker'
    type = 'date'


@grok.adapter(
    zope.schema.interfaces.IDate,
    icemac.addressbook.browser.interfaces.IAddressBookLayer)
@grok.implementer(z3c.form.interfaces.IFieldWidget)
def DateFieldWidget(field, request):
    """Factory for DateWidget."""
    return z3c.form.widget.FieldWidget(field, DateWidget(request))


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.ITimeWidget)
class TimeWidget(DatetimeWidgetBase):
    """Widget to enter time using JavaScript picker."""

    klass = 'time-widget'
    picker_js_func_name = 'timepicker'
    type = 'time'


@grok.adapter(
    zope.schema.interfaces.ITime,
    icemac.addressbook.browser.interfaces.IAddressBookLayer)
@grok.implementer(z3c.form.interfaces.IFieldWidget)
def TimeFieldWidget(field, request):
    """Factory for TimeWidget."""
    return z3c.form.widget.FieldWidget(field, TimeWidget(request))


class DateDataConverter(z3c.form.converter.DateDataConverter):
    """Special date converter which does not have a year 2k problem."""

    length = 'medium'


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IImageSelectWidget)
class ImageSelectWidget(z3c.form.browser.select.SelectWidget):
    """Select widget displays images as selectables."""

    def update(self):
        super(ImageSelectWidget, self).update()
        jqueryui_css.need()
        ui_selectable.need()


@grok.adapter(zope.schema.interfaces.IChoice,
              icemac.addressbook.interfaces.IImageSource,
              icemac.addressbook.browser.interfaces.IAddressBookLayer)
@grok.implementer(z3c.form.interfaces.IFieldWidget)
def SelectFieldWidget(field, source, request):
    """`IFieldWidget` factory for SelectWidget."""
    return z3c.form.widget.FieldWidget(field, ImageSelectWidget(request))

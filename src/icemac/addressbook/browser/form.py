# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
from datetime import datetime
import pytz
import z3c.form.converter
import zope.component
import zope.preference.interfaces


class DatetimeDataConverter(z3c.form.converter.DatetimeDataConverter):
    """Converter for z3c.form displaying localized date times.

    Converts stored datetimes to timezone of request.
    Converts datetimes from form to store with time zone of request.

    """
    @property
    def time_zone_name(self):
        """User selected time zone name."""
        return zope.component.getUtility(
            zope.preference.interfaces.IPreferenceGroup,
            name="ab.timeZone").time_zone

    def toWidgetValue(self, value):
        """Convert to time zone user has selected."""
        if value is not self.field.missing_value and value.tzinfo is not None:
            value = value.astimezone(pytz.timezone(self.time_zone_name))
        return super(DatetimeDataConverter, self).toWidgetValue(value)

    def toFieldValue(self, value):
        value = super(DatetimeDataConverter, self).toFieldValue(value)
        if value is None:
            return value
        return datetime(*value.timetuple()[:6],
                        tzinfo=pytz.timezone(self.time_zone_name))

from mock import patch, Mock
import unittest2 as unittest


class DatetimeDataConverterTests(unittest.TestCase):
    """Testing ..form.DatetimeDataConverter."""

    def setUp(self):
        from gocept.testing.mock import Property
        super(DatetimeDataConverterTests, self).setUp()
        time_zone_name = ('icemac.addressbook.browser.form.'
                          'DatetimeDataConverter.time_zone_name')
        patcher = patch(time_zone_name, Property())
        time_zone_name = patcher.start()
        time_zone_name.return_value = 'Etc/GMT-4'
        self.addCleanup(patcher.stop)

    def make_one(self):
        from zope.publisher.browser import TestRequest
        from ..form import DatetimeDataConverter
        widget = Mock()
        widget.request = TestRequest()
        field = Mock()
        field.missing_value = None
        return DatetimeDataConverter(field, widget)

    def test_toWidgetValue_renders_datetime_with_tz_localized(self):
        from datetime import datetime
        from pytz import utc
        self.assertEqual(
            u'13/02/01 21:20',
            self.make_one().toWidgetValue(
                datetime(2013, 2, 1, 17, 20, tzinfo=utc)))

    def test_toWidgetValue_renders_native_datetime_unchanged(self):
        from datetime import datetime
        from pytz import utc
        self.assertEqual(
            u'13/02/01 17:20',
            self.make_one().toWidgetValue(datetime(2013, 2, 1, 17, 20)))

    def test_toWidgetValue_renders_missing_value_as_empty_string(self):
        self.assertEqual(u'', self.make_one().toWidgetValue(None))

    def test_toFieldValue_adds_tzinfo(self):
        from datetime import datetime
        from pytz import timezone
        self.assertEqual(
            datetime(2013, 2, 1, 21, 20, tzinfo=timezone('Etc/GMT-4')),
            self.make_one().toFieldValue(u'13/02/01 21:20'))

    def test_toFieldValue_leaves_empty_value_alone(self):
        from datetime import datetime
        from pytz import timezone
        self.assertIsNone(self.make_one().toFieldValue(u''))

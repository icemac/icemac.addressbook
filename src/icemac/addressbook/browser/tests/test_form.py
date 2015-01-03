from mock import patch, Mock
import icemac.addressbook.testing
import unittest


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


class ZopeI18nPatternToJqueryPatternTests(unittest.TestCase):
    """Testing ..form.zope_i18n_pattern_to_jquery_pattern()."""

    def callFUT(self, pattern):
        from ..form import zope_i18n_pattern_to_jquery_pattern
        return zope_i18n_pattern_to_jquery_pattern(pattern)

    def test_converts_German_date_format_correctly(self):
        self.assertEqual('dd.mm.y HH:mm', self.callFUT('dd.MM.yy HH:mm'))

    def test_converts_American_date_format_correctly(self):
        self.assertEqual('m/d/y hh:mm TT', self.callFUT('M/d/yy h:mm a'))


class DatetimeWidgetTests(icemac.addressbook.testing.SeleniumTestCase):
    """Selenium testing ..form.DatetimeWidget."""

    def setUp(self):
        from icemac.addressbook.testing import create_field, create_keyword
        super(DatetimeWidgetTests, self).setUp()
        ab = self.layer['addressbook']
        keyword_entity_name = 'icemac.addressbook.keyword.Keyword'
        create_field(ab, keyword_entity_name, 'Datetime', u'datetime')
        self.kw = create_keyword(ab, u'foobar')

    def test_datetime_widget_renders_javascript_calendar(self):
        self.login('editor', 'editor')
        s = self.selenium
        s.open('/ab/++attribute++keywords/%s' % self.kw.__name__)
        # Activate the datetime field which opens the JavaScript calendar
        s.click('id=form-widgets-Field-1')
        # Click the `now` button:
        s.click("//button[@type='button']")
        # And the `done` button:
        s.click("xpath=(//button[@type='button'])[2]")
        # Save the form:
        s.clickAndWait("id=form-buttons-apply")
        # Successful apply leads back to keyword overview
        s.assertLocation('http://%s/ab/++attribute++keywords' % s.server)


class DateWidgetTests(icemac.addressbook.testing.SeleniumTestCase):
    """Selenium testing ..form.DateWidget."""

    def test_date_widget_renders_javascript_calendar(self):
        self.login('editor', 'editor')
        s = self.selenium
        s.open('/ab/@@addPerson.html')
        # Activate the date field which opens the JavaScript calendar
        s.click('id=IcemacAddressbookPersonPerson-widgets-'
                'IcemacAddressbookPersonPerson-birth_date')
        # Click the first of the first month:
        s.click("link=1")
        # Fill in required fiels:
        s.type('id=IcemacAddressbookPersonPerson-widgets-'
               'IcemacAddressbookPersonPerson-last_name', 'Tester')
        # Save the form:
        s.clickAndWait("id=form-buttons-add")
        # Successful apply leads back to keyword overview
        s.assertLocation('http://%s/ab/@@person-list.html' % s.server)

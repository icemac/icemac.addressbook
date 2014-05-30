import icemac.addressbook.testing
import unittest


class TimeZoneTests(unittest.TestCase,
                    icemac.addressbook.testing.BrowserMixIn):
    """Testing time zone preferences."""

    layer = icemac.addressbook.testing.TEST_BROWSER_LAYER

    def get_browser(
            self, url='http://localhost/ab/++preferences++/ab.timeZone'):
        browser = super(TimeZoneTests, self).get_browser('visitor')
        browser.open(url)
        return browser

    def test_default_value_is_UTC(self):
        self.assertEqual(
            ['UTC'], self.get_browser().getControl('Time zone').displayValue)

    def test_changed_value_is_stored(self):
        browser = self.get_browser()
        browser.getControl('Time zone').displayValue = ['Europe/Berlin']
        browser.getControl('Apply').click()
        self.assertIn('Data successfully updated.', browser.contents)
        self.assertEqual(
            ['Europe/Berlin'], browser.getControl('Time zone').displayValue)

    def test_metadata_is_converted_to_selected_time_zone(self):
        from datetime import datetime
        from icemac.addressbook.testing import create_keyword
        from pytz import utc
        from zope.dublincore.interfaces import IZopeDublinCore
        from zope.component import getUtility
        from zope.preference.interfaces import IDefaultPreferenceProvider

        kw = create_keyword(self.layer['addressbook'], u'foo')
        IZopeDublinCore(kw).modified = datetime(2001, 1, 1, tzinfo=utc)
        default_prefs = getUtility(IDefaultPreferenceProvider)
        default_prefs.getDefaultPreferenceGroup('ab.timeZone').time_zone = (
            'Asia/Aden')

        browser = self.get_browser(
            'http://localhost/ab/++attribute++keywords/%s' % kw.__name__)
        self.assertIn('01/01/01 03:00', browser.contents)
        self.assertIn('Modification Date (Asia/Aden)', browser.contents)
        self.assertIn('Creation Date (Asia/Aden)', browser.contents)

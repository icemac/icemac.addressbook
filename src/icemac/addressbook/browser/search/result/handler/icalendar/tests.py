from icemac.addressbook.browser.testing import (
    WSGI_SEARCH_LAYER, search_for_persons_with_keyword_search_using_browser)
from mock import patch
import icemac.addressbook.testing


class ExportBrowserSTests(icemac.addressbook.testing.BrowserTestCase):
    """Smoke browser testing ..export.*"""

    layer = WSGI_SEARCH_LAYER

    def test_exports_ical_file(self):
        browser = search_for_persons_with_keyword_search_using_browser(
            'family', login='visitor')
        browser.getControl('Apply on selected persons').displayValue = ['iCal']
        browser.handleErrors = False
        with patch('pkg_resources.get_distribution') as get_distribution:
            get_distribution().version = '1.2.3'
            browser.getControl(name='form.buttons.apply').click()
        self.assertEqual(
            ['BEGIN:VCALENDAR',
             'VERSION:2.0',
             'PRODID:-//icemac.addressbook//1.2.3//EN',
             'CALSCALE:GREGORIAN',
             'X-WR-CALNAME:birthdays of None',
             'BEGIN:VEVENT',
             'SUMMARY:Koch',
             'DTSTART;VALUE=DATE:19520124',
             'DTEND;VALUE=DATE:19520125',
             'UID:http://localhost/ab/Person-2/iCalendar',
             'RRULE:FREQ=YEARLY',
             'END:VEVENT',
             'END:VCALENDAR',
             ''], browser.contents.split('\r\n'))

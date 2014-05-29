from mock import patch
import icemac.addressbook.browser.testing
import icemac.addressbook.testing


class iCalendarTests(icemac.addressbook.testing.BrowserTestCase):
    """Testing ..icalendar.iCalendar."""

    layer = icemac.addressbook.browser.testing.WSGI_SEARCH_LAYER

    def test_view_returns_iCalendar_file_of_birthday(self):
        browser = self.get_browser('visitor')
        browser.open('http://localhost/ab/@@person-list.html')
        browser.getLink('Liese').click()
        browser.handleErrors = False
        browser.getControl('Export').click()
        with patch('pkg_resources.get_distribution') as get_distribution:
            get_distribution().version = '1.2.3'
            browser.getLink('iCalendar').click()
        self.assertEqual(
            ['BEGIN:VCALENDAR',
             'VERSION:2.0',
             'PRODID:-//icemac.addressbook//1.2.3//EN',
             'CALSCALE:GREGORIAN',
             'BEGIN:VEVENT',
             'SUMMARY:Tester\\, Liese',
             'DTSTART;VALUE=DATE:19761115',
             'DTEND;VALUE=DATE:19761116',
             'UID:http://localhost/ab/Person-5/@@iCalendar',
             'RRULE:FREQ=YEARLY',
             'END:VEVENT',
             'END:VCALENDAR',
             ''], browser.contents.split('\r\n'))

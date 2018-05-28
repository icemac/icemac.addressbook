from mock import patch


def test_icalendar__iCalendar__1(search_data, browser):
    """The view returns an iCalendar file containing the birthday."""
    browser.login('visitor')
    browser.open(browser.PERSONS_LIST_URL)
    browser.getLink('Liese').click()
    browser.getControl('Export').click()
    with patch('pkg_resources.get_distribution') as get_distribution:
        get_distribution().version = '1.2.3'
        browser.getLink('iCalendar').click()
    assert ['BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//icemac.addressbook//1.2.3//EN',
            'CALSCALE:GREGORIAN',
            'BEGIN:VEVENT',
            'SUMMARY:Tester\\, Liese (*1976)',
            'DTSTART;VALUE=DATE:19761115',
            'DTEND;VALUE=DATE:19761116',
            'UID:http://localhost/ab/Person-5/@@iCalendar',
            'RRULE:FREQ=YEARLY',
            'END:VEVENT',
            'END:VCALENDAR',
            ''] == browser.contents.split('\r\n')

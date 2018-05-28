from mock import patch


def test_iCalendar__1(search_data, browser):
    """Smoke testing that an iCal file gets exported."""
    browser.login('visitor')
    with patch('pkg_resources.get_distribution') as get_distribution:
        get_distribution().version = '1.2.3'
        browser.keyword_search('family', apply='iCal')
    assert ['BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//icemac.addressbook//1.2.3//EN',
            'CALSCALE:GREGORIAN',
            'X-WR-CALNAME:birthdays of test addressbook',
            'BEGIN:VEVENT',
            'SUMMARY:Koch (*1952)',
            'DTSTART;VALUE=DATE:19520124',
            'DTEND;VALUE=DATE:19520125',
            'UID:http://localhost/ab/Person-2/@@iCalendar',
            'RRULE:FREQ=YEARLY',
            'END:VEVENT',
            'END:VCALENDAR',
            ''] == browser.contents.split('\r\n')

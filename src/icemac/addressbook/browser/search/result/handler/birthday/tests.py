from datetime import date
from gocept.testing.mock import Property
from mock import patch
import pytest


@pytest.fixture(scope='function')
def birthdates_data(address_book, PersonFactory):
    """Create the data for the `Birthdays` tests."""
    return [
        PersonFactory(
            address_book,
            u'Vrozzek',
            first_name=u'Paul',
            birth_date=date(2000, 5, 3)),
        PersonFactory(
            address_book,
            u'Vranzz',
            first_name=u'Peter',
            birth_date=date(1995, 5, 3)),
        PersonFactory(
            address_book,
            u'Youngster',
            first_name=u'Yvonne',
            birth_date=date(2003, 4, 4)),
    ]


def test_birthday__Birthdays__1(birthdates_data, browser):
    """`Birthdays` returns a table of names and birth dates:

    - sorted by month, day, year
    - the number of entries in the table.

    """
    browser.login('visitor')
    persons = (
        'icemac.addressbook.browser.search.result.handler.birthday.Birthdays.'
        'persons')
    with patch(persons, Property()) as persons:
        persons.return_value = birthdates_data
        browser.open('http://localhost/ab/@@person-birthdays.html')
        assert [
            'Yvonne Youngster',
            '2003 4 4 ',
            'Peter Vranzz',
            '1995 5 3 ',
            'Paul Vrozzek',
            '2000 5 3 '] == browser.etree.xpath('//table/tbody/tr/td/text()')
        assert 'Number of persons: 3' in browser.contents

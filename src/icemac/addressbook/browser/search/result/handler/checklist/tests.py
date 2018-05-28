import pytest
from mock import patch


@pytest.fixture(scope='function')
def checklist_data(address_book, PersonFactory):
    """Create the data for the `Checklist` tests."""
    return [PersonFactory(address_book, u'Vrozzek', first_name=u'Paul'),
            PersonFactory(address_book, u'Vranzz', first_name=u'Peter')]


def test_checklist__Checklist__1(checklist_data, browser):
    """It returns a list of check-boxes and names plus a count."""
    from gocept.testing.mock import Property
    browser.login('visitor')
    persons = (
        'icemac.addressbook.browser.search.result.handler.checklist.Checklist.'
        'persons')
    with patch(persons, Property()) as persons:
        persons.return_value = checklist_data
        browser.open('http://localhost/ab/@@person-checklist.html')
        assert browser.getControl('Paul Vrozzek').selected is False
        assert browser.getControl('Peter Vranzz').selected is False
        assert 'Number of persons: 2' in browser.contents

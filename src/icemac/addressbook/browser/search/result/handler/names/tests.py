import pytest
from mock import patch


@pytest.fixture(scope='function')
def names_data(address_book, PersonFactory):
    """Create the data for the `Names` tests."""
    return [PersonFactory(address_book, u'Vrozzek', first_name=u'Paul'),
            PersonFactory(address_book, u'Vranzz', first_name=u'Peter')]


def test_names__Names__1(names_data, browser):
    """`Names` returns a comma separated list of names and a count."""
    from gocept.testing.mock import Property
    browser.login('visitor')
    persons = (
        'icemac.addressbook.browser.search.result.handler.names.Names.'
        'persons')
    with patch(persons, Property()) as persons:
        persons.return_value = names_data
        browser.open('http://localhost/ab/@@person-names.html')
        assert 'Paul Vrozzek, Peter Vranzz' in browser.contents
        assert 'Number of persons: 2' in browser.contents

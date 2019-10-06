# -*- coding: utf-8 -*-
from icemac.addressbook.interfaces import IPerson, IPostalAddress
import decimal
import pytest


KEYWORD = u'keyword for test'


# Fixtures to create objects:

@pytest.fixture(scope='function')
def UpdateablePersonFactory(FullPersonFactory):
    """Return a callable which creates a person object that can be updated.

    Supports user defined fields and sets a default keyword if `keywords` is
    not in the parameters of the call.

    """
    def create_updateable_person(address_book, **kw):
        kw.setdefault('keywords', [KEYWORD])
        kw.setdefault('last_name', u'Tester')
        return FullPersonFactory(address_book, **kw)
    return create_updateable_person


@pytest.fixture(scope='function')
def AddressWithUserdefinedFieldFactory(
        FieldFactory, UpdateablePersonFactory, PostalAddressFactory):
    """Callable to create an address on a person with a user defined field."""
    def _create_user_defined_field(address_book, field_type, field_value):
        """Create a user defined field."""
        field_name = FieldFactory(
            address_book, IPostalAddress, field_type, u'distance').__name__
        return PostalAddressFactory(
            UpdateablePersonFactory(address_book),
            **{field_name: field_value, 'set_as_default': True})
    return _create_user_defined_field


# Helper functions

def _update_field_value(browser, field_name, operator, value):
    """Update a field using the update search result handler."""
    browser.login('mgr')
    browser.keyword_search(KEYWORD, apply='Update')
    browser.getControl('field').displayValue = [field_name]
    browser.getControl('Next').click()
    assert '' == browser.getControl('new value', index=0).value
    browser.getControl('new value', index=0).value = value
    browser.getControl('operation').displayValue = [operator]
    browser.getControl('Next').click()


# Tests

def test_update__endtoend__1(search_data, browser):
    """Testing updating selected persons end to end.

    The `update` search result handler allows to update a single field on each
    selected person.

    """
    # The `searchDataS` fixture defines some persons. When user searches for
    # them all persons are selected by default so he only has to select the
    # `update` search handler to perform a multi-update:
    browser.login('mgr')
    browser.keyword_search('family', apply='Update')

    # The user is guided through the update using a wizard.
    # 1st) Choose a field for update:
    assert ['person -- first name', 'person -- last name',
            'person -- birth date'] == browser.getControl(
                'field').displayOptions[:3]
    browser.getControl('field').displayValue = ['person -- notes']
    browser.getControl('Next').click()

    # 2nd) Enter a new value for the selected field and choose an operation
    # which defaults to 'append':
    assert ['append new value to existing one'] == browser.getControl(
        'operation').displayValue
    browser.getControl('new value', index=0).value = '\tfoobar'
    browser.getControl('Next').click()

    # 3rd) Check result:
    assert 2 == browser.contents.count('\tfoobar')

    # 4th) Hitting `Complete` persists the change and redirects to the person
    # list, displaying a message:
    browser.getControl('Complete').click()
    assert browser.PERSONS_LIST_URL == browser.url
    assert 'Data successfully updated.' == browser.message

    # The fields got changed as promised in the message:
    browser.getLink('Person list').click()
    browser.getLink('Koch').click()
    assert 'father-in-law\tfoobar' == browser.getControl('notes').value


def test_update__endtoend__2(search_data, browser):
    """Adding an empty new value does not change the updated value.

    This is an edge case test.

    """
    browser.login('mgr')
    browser.keyword_search('family', apply='Update')
    browser.getControl('field').displayValue = ['person -- last name']
    browser.getControl('Next').click()
    browser.getControl('new value', index=0).value = ''
    browser.getControl('operation').displayValue = [
        'append new value to existing one']
    browser.getControl('Next').click()
    # The last name column is displayed as a link column it contains the
    # unchanged last name:
    assert ('<td><a href="http://localhost/ab/Person-2">Koch</a></td>' in
            browser.contents)


def test_update__endtoend__3(
        address_book, FieldFactory, UpdateablePersonFactory, browser):
    """A user defined boolean field can be updated."""
    field_name = FieldFactory(
        address_book, IPerson, 'Bool', u'Ever met').__name__
    UpdateablePersonFactory(address_book, **{field_name: False})
    browser.login('mgr')
    browser.keyword_search(KEYWORD, apply='Update')
    browser.getControl('field').displayValue = ['person -- Ever met']
    browser.getControl('Next').click()
    browser.getControl('yes').click()
    browser.getControl('operation').displayValue = [
        'replace existing value with new one']
    browser.getControl('Next').click()
    # Update sets the value to 'yes':
    assert '<td>Tester</td><td>yes</td>' in browser.contents_without_whitespace


def test_update__endtoend__4(
        address_book, FieldFactory, UpdateablePersonFactory,
        PostalAddressFactory, browser):
    """A user defined choice field can be updated."""
    field_name = FieldFactory(
        address_book, IPostalAddress, 'Choice', u'distance',
        values=[u'< 50 km', u'>= 50 km']).__name__
    PostalAddressFactory(UpdateablePersonFactory(address_book),
                         **{field_name: '>= 50 km', 'set_as_default': True})

    browser.login('mgr')
    browser.keyword_search(KEYWORD, apply='Update')
    browser.getControl('field').displayValue = ['postal address -- distance']
    browser.getControl('Next').click()
    assert ['No value', '< 50 km', '>= 50 km'] == browser.getControl(
        'new value').displayOptions
    browser.getControl('new value').displayValue = ['< 50 km']
    browser.getControl('operation').displayValue = [
        'replace existing value with new one']
    browser.getControl('Next').click()
    # Update sets the value to '< 50 km':
    assert ('<td>Tester</td><td><50km</td>' in
            browser.contents_without_whitespace)


def test_update__endtoend__5(address_book, UpdateablePersonFactory, browser):
    """The keywords field can be updated."""
    UpdateablePersonFactory(address_book, keywords=[KEYWORD, u'second kw'])
    browser.login('mgr')
    browser.keyword_search('second kw', apply='Update')
    browser.getControl('field').displayValue = ['person -- keywords']
    browser.getControl('Next').click()
    assert [KEYWORD, 'second kw'] == browser.getControl(
        'new value').displayOptions
    browser.getControl('new value').displayValue = ['second kw']
    browser.getControl('operation').displayValue = [
        'remove selected keywords from existing ones']
    browser.getControl('Next').click()
    assert ('<td>Tester</td><td>keywordfortest</td>' in
            browser.contents_without_whitespace)
    browser.getControl('Complete').click()
    # After removing the keyword from the person no person can be found:
    browser.keyword_search(u'second kw')
    assert 'No person found.' in browser.contents


@pytest.mark.parametrize("type,factory", (
    ['Int', int],
    ['Decimal', decimal.Decimal]))
def test_update__endtoend__6(
        address_book, AddressWithUserdefinedFieldFactory, browser, type,
        factory):
    """A user defined integer field can be updated."""
    AddressWithUserdefinedFieldFactory(address_book, type, factory(50))
    _update_field_value(browser, 'postal address -- distance', 'add', '5')
    assert '<td>Tester</td><td>55</td>' in browser.contents_without_whitespace


def test_update__endtoend__7(
        address_book, UpdateablePersonFactory, EMailAddressFactory, browser):
    """Validation errors show up in the result table."""
    EMailAddressFactory(
        UpdateablePersonFactory(address_book), set_as_default=True)
    _update_field_value(
        browser, 'e-mail address -- e-mail address', 'append', 'foo')
    assert ('<td>Tester</td><td></td><td>None</td>'
            '<td>fooisnotavalide-mailaddress.</td>' in
            browser.contents_without_whitespace)
    # Complete button is not shown:
    assert ['form.buttons.back'] == browser.submit_control_names


def test_update__endtoend__8(
        address_book, AddressWithUserdefinedFieldFactory, browser):
    """Division by zero is handled like a validation error."""
    AddressWithUserdefinedFieldFactory(address_book, 'Int', 50)
    _update_field_value(browser, 'postal address -- distance', 'div', '0')
    assert ('<td>Tester</td><td>50</td><td>50</td><td>Divisionbyzero</td>' in
            browser.contents_without_whitespace)
    # Complete button is not shown:
    assert ['form.buttons.back'] == browser.submit_control_names


def test_update__endtoend__9(address_book, UpdateablePersonFactory, browser):
    """Field selected for change can be changed."""
    UpdateablePersonFactory(address_book)
    _update_field_value(browser, 'person -- first name', 'append', 'foo')
    browser.getControl('Back').click()
    browser.getControl('Back').click()
    browser.getControl('field').displayValue = ['person -- birth date']
    browser.getControl('Next').click()
    # The newly selected field for update might have a data types which does
    # not match the previous selected on, so the value is deleted
    assert '' == browser.getControl('new value').value


def test_update__endtoend__10(address_book, UpdateablePersonFactory, browser):
    """Not hitting the `complete button` does not persist any changes."""
    UpdateablePersonFactory(address_book)
    _update_field_value(browser, 'person -- last name', 'append', 'foo')
    browser.getLink('Person list').click()
    # The last name of person 'Tester' is unchanged:
    assert ('<a href="{0.PERSON_EDIT_URL}">Tester</a>'.format(browser) in
            browser.contents)


def test_update__endtoend__11(address_book, UpdateablePersonFactory, browser):
    """If the user selects a step with data missing he gets redirected back."""
    UpdateablePersonFactory(address_book)
    browser.login('mgr')
    browser.keyword_search(KEYWORD, apply='Update')
    assert browser.SEARCH_MULTI_UPDATE_URL == browser.url
    browser.getLink('New value').click()
    # 'chooseField' is the first step, so we get redirected there
    assert browser.SEARCH_MULTI_UPDATE_CHOOSE_FIELD_URL == browser.url
    browser.getLink('Check result').click()
    assert browser.SEARCH_MULTI_UPDATE_CHOOSE_FIELD_URL == browser.url
    browser.getControl('field').displayValue = ['person -- first name']
    browser.getControl('Next').click()
    assert browser.SEARCH_MULTI_UPDATE_ENTER_VALUE_URL == browser.url
    browser.getLink('Choose field').click()
    assert browser.SEARCH_MULTI_UPDATE_CHOOSE_FIELD_URL == browser.url
    browser.getLink('Check result').click()
    # After selecting the field 'enterValue' is complete, as the only
    # required field has a default value
    assert browser.SEARCH_MULTI_UPDATE_CHECK_RESULT_URL == browser.url
    # There is no 'complete' button as the user did not enter data in step
    # 'enterValue':
    assert ['form.buttons.back'] == browser.submit_control_names

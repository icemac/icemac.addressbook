# -*- coding: utf-8 -*-
import pytest


def test_address__menu__1(person_data, browser):
    """The entries in the add menu have a specific sort order."""
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    assert ['postal address',
            'phone number',
            'e-mail address',
            'home page',
            'file'] == browser.etree.xpath(
        '//ul[@id="add-menu-content"]/li/a/span/text()')


def test_address__AddPhoneNumberForm__1(person_data, browser):
    """`AddPhoneNumberForm` allows to add another phone number."""
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getLink('phone number').click()
    browser.getControl('number').value = '+4901761234567'
    browser.getControl('Add').click()
    assert '"+4901761234567" added.' == browser.message
    # After adding a new phone number, the person edit form is displayed
    # where the new phone number is shown:
    assert '+4901761234567' == browser.getControl('number', index=2).value
    # It is now possible to change this phone number in the person edit form:
    browser.getControl('number', index=2).value = '+4901767654321'
    browser.getControl('Save').click()
    'Data successfully updated.' == browser.message
    browser.open(browser.PERSON_EDIT_URL)
    assert '+4901767654321' == browser.getControl('number', index=2).value


def test_address__AddPostalAddressForm__1(person_data, browser):
    """`AddPostalAddressForm` allows to add another postal address."""
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getLink('postal address').click()
    browser.getControl('address prefix').value = 'ABC-Computer'
    browser.getControl('street').value = 'Forsterstraße 302a'
    browser.getControl('city').value = 'Erfurt'
    browser.getControl('zip').value = '98344'
    browser.getControl('Add').click()
    assert (
        u'"ABC-Computer, Forsterstraße 302a, 98344, Erfurt, Germany" added.' ==
        browser.message)
    # After adding a new postal address, the person edit form is displayed
    # where the new postal address is shown:
    assert 'ABC-Computer' == browser.getControl(
        'address prefix', index=2).value
    assert 'Forsterstraße 302a' == browser.getControl('street', index=1).value
    assert 'Erfurt' == browser.getControl('city', index=2).value
    # It is now possible to change this postal address in the person edit form:
    browser.getControl('address prefix', index=2).value = 'RST-Software'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    browser.open(browser.PERSON_EDIT_URL)
    assert 'RST-Software' == browser.getControl(
        'address prefix', index=2).value


def test_address__AddEMailAddressForm__1(person_data, browser):
    """`AddEMailAddressForm` allows to add another e-mail address."""
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getLink('e-mail address').click()
    browser.getControl('e-mail address').value = 'pt@abc-computer.de'
    browser.getControl('Add').click()
    assert '"pt@abc-computer.de" added.' == browser.message
    # After adding a new e-mail address, the person edit form is displayed
    # where the new e-mail address is shown:
    assert 'pt@abc-computer.de' == browser.getControl(
        'e-mail address', index=3).value
    # It is now possible to change this e-mail address in the person edit form:
    browser.getControl('e-mail address', index=3).value = 'pt@rst.example.edu'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    browser.open(browser.PERSON_EDIT_URL)
    assert 'pt@rst.example.edu' == browser.getControl(
        'e-mail address', index=3).value


def test_address__AddHomePageAddressForm__1(person_data, browser):
    """`AddHomePageAddressForm` allows to add another home page address."""
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getLink('home page').click()
    browser.getControl('URL').value = 'http://www.abc-computer.de'
    browser.getControl('Add').click()
    assert '"http://www.abc-computer.de" added.' == browser.message
    # After adding a new home page address, the person edit form is
    # displayed where the new home page address is shown:
    assert 'http://www.abc-computer.de' == browser.getControl(
        'URL', index=2).value
    # It is now possible to change this home page address in the person edit
    # form:
    browser.getControl('URL', index=2).value = 'http://www.rst.example.edu'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    browser.open(browser.PERSON_EDIT_URL)
    assert 'http://www.rst.example.edu' == browser.getControl(
        'URL', index=1).value


def test_address__DeletePostalAddressForm__1(person_data, browser):
    """`DeletePostalAddressForm` allows to delete a home page address."""
    browser.login('editor')
    browser.open(browser.PERSON_DELETE_ENTRY_URL)
    browser.getControl('RST-Software').click()
    browser.getControl('Delete entry').click()
    assert browser.POSTAL_ADDRESS_DELETE_URL == browser.url
    browser.getControl('Yes').click()
    assert (u'"RST-Software, Forsterstra\xdfe 302a, 98344, Erfurt, Germany" '
            u'deleted.' == browser.message)
    assert browser.PERSON_EDIT_URL
    assert (['c/o Mama, Demoweg 23, 88888, Testhausen, Austria'] ==
            browser.getControl('main postal address').displayOptions)


def test_address__DeletePostalAddressForm__2(person_data, browser):
    """`DeletePostalAddressForm` can be canceled."""
    browser.login('editor')
    browser.open(browser.PERSON_DELETE_ENTRY_URL)
    browser.getControl('RST-Software').click()
    browser.getControl('Delete entry').click()
    browser.getControl('No, cancel').click()
    assert 'Deletion canceled.' == browser.message
    assert browser.PERSON_EDIT_URL == browser.url


def test_address__DeletePostalAddressForm__3(person_data, browser):
    """Deleting the main address creates a new, empty address."""
    browser.login('editor')
    browser.open(browser.PERSON_DELETE_ENTRY_URL)
    browser.getControl('Entries').displayValue = [
        'postal address -- c/o Mama, Demoweg 23, 88888, Testhausen, Austria']
    browser.getControl('Delete entry').click()
    browser.getControl('Yes').click()
    assert ('"c/o Mama, Demoweg 23, 88888, Testhausen, Austria" deleted.' ==
            browser.message)
    assert browser.PERSON_EDIT_URL == browser.url
    assert (['Germany'] ==
            browser.getControl('main postal address').displayValue)
    assert (
        ['RST-Software, Forsterstra\xc3\x9fe 302a, 98344, Erfurt, Germany',
         'Germany'] ==
        browser.getControl('main postal address').displayOptions)


@pytest.mark.parametrize('loginname', ['visitor', 'archivist'])
def test_address__DeletePostalAddressForm__4(person_data, browser, loginname):
    """It cannot be accessed by some roles."""
    browser.login(loginname)
    browser.assert_forbidden(browser.POSTAL_ADDRESS_DELETE_URL)


def test_address__DeletePhoneNumberForm__1(person_data, browser):
    """`DeletePhoneNumberForm` allows to delete a phone number."""
    browser.login('editor')
    browser.open(browser.PERSON_DELETE_ENTRY_URL)
    browser.getControl('+4901761234567').click()
    browser.getControl('Delete entry').click()
    assert browser.PHONE_NUMBER_DELETE_URL == browser.url
    browser.getControl('Yes').click()
    assert ('"+4901761234567" deleted.' == browser.message)
    assert browser.PERSON_EDIT_URL
    assert (['+4901767654321'] ==
            browser.getControl('main phone number').displayOptions)


@pytest.mark.parametrize('loginname', ['visitor', 'archivist'])
def test_address__DeletePhoneNumberForm__2(person_data, browser, loginname):
    """It cannot be accessed by some roles."""
    browser.login(loginname)
    browser.assert_forbidden(browser.PHONE_NUMBER_DELETE_URL)


def test_address__DeleteEMailAddressForm__1(person_data, browser):
    """`DeleteEMailAddressForm` allows to delete an email address."""
    browser.login('editor')
    browser.open(browser.PERSON_DELETE_ENTRY_URL)
    browser.getControl('pt@rst.example.edu').click()
    browser.getControl('Delete entry').click()
    assert browser.EMAIL_ADDRESS_DELETE_URL == browser.url
    browser.getControl('Yes').click()
    assert ('"pt@rst.example.edu" deleted.' == browser.message)
    assert browser.PERSON_EDIT_URL
    assert (['petra@example.com'] ==
            browser.getControl('main e-mail address').displayOptions)


@pytest.mark.parametrize('loginname', ['visitor', 'archivist'])
def test_address__DeleteEMailAddressForm__2(person_data, browser, loginname):
    """It cannot be accessed by some roles."""
    browser.login(loginname)
    browser.assert_forbidden(browser.EMAIL_ADDRESS_DELETE_URL)


def test_address__DeleteHomePageAddressForm__1(person_data, browser):
    """`DeleteHomePageAddressForm` allows to delete a home page address."""
    browser.login('editor')
    browser.open(browser.PERSON_DELETE_ENTRY_URL)
    browser.getControl('http://www.rst.example.edu').click()
    browser.getControl('Delete entry').click()
    assert browser.HOMEPAGE_ADDRESS_DELETE_URL == browser.url
    browser.getControl('Yes').click()
    assert ('"http://www.rst.example.edu" deleted.' == browser.message)
    assert browser.PERSON_EDIT_URL
    assert (['http://petra.example.com'] ==
            browser.getControl('main home page address').displayOptions)


@pytest.mark.parametrize('loginname', ['visitor', 'archivist'])
def test_address__DeleteHomePageAddressForm__2(
        person_data, browser, loginname):
    """It cannot be accessed by some roles."""
    browser.login(loginname)
    browser.assert_forbidden(browser.HOMEPAGE_ADDRESS_DELETE_URL)

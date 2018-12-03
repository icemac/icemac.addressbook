from mock import patch
from z3c.flashmessage.interfaces import IMessageSource
import datetime
import icemac.addressbook.browser.messages.messages
import pytest
import zope.component
import zope.publisher.testing


@pytest.yield_fixture('function')
def fake_message_source(empty_zodb):
    """Fake message source to be not user dependent."""
    UserSpecificRAMMessageSource = (
        icemac.addressbook.browser.messages.messages
        .UserSpecificRAMMessageSource)
    with patch.object(UserSpecificRAMMessageSource, '_get_storage') as storage:
        storage.return_value = []
        yield


def send_msg(msg):
    """Send a flash message."""
    with zope.publisher.testing.interaction('zope.mgr'):
        zope.component.getUtility(IMessageSource).send(msg)


def test_testing__Browser__message__1(fake_message_source, browser):
    """It is an empty list if there are no flash messages."""
    browser.login('mgr')
    browser.open('http://localhost')
    assert [] == browser.message


def test_testing__Browser__message__2(fake_message_source, browser):
    """It is a string if there is exactly one flash message."""
    send_msg('foo')
    browser.login('mgr')
    browser.handleErrors = False
    browser.open('http://localhost')
    assert 'foo' == browser.message


def test_testing__Browser__message__3(fake_message_source, browser):
    """It is a list of strings if there is more than one flash message."""
    send_msg('foo')
    send_msg('blah')
    browser.login('mgr')
    browser.open('http://localhost')
    assert ['foo', 'blah'] == browser.message


def test_testing__DateTimeClass__format__1(DateTime):
    """It formats a date as zope.testbrowser expects it."""
    assert '2017 1 27 ' == DateTime.format(datetime.date(2017, 1, 27))


def test_testing__SeleniumLogin__1(address_book, browser):
    """It cannot be accessed by an anonymous user."""
    with pytest.raises(zope.testbrowser.browser.HTTPError) as err:
        browser.open(browser.SELENIUM_LOGIN_URL)
    assert 'HTTP Error 401: Unauthorized' == str(err.value)

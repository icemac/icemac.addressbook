from mock import patch
from z3c.flashmessage.interfaces import IMessageSource
from zope.authentication.interfaces import IAuthentication
import contextlib
import pytest
import zope.component
import zope.security.management
import zope.security.testing


@pytest.yield_fixture('function')
def fake_session(empty_zodb):
    """Fake a user session to be static."""
    with patch('zope.session.interfaces.ISession') as ISession:
        ISession.return_value = {'z3c.flashmessage': {}}
        yield


@contextlib.contextmanager
def fake_interaction(loginname):
    """Fake an interaction for a user."""
    auth = zope.component.getUtility(IAuthentication)
    principal = auth.getPrincipalByLogin(loginname)
    participation = zope.security.testing.Participation(principal)
    zope.security.management.newInteraction(participation)
    yield
    zope.security.management.endInteraction()


def send_msg(msg):
    """Send a flash message."""
    with fake_interaction('mgr'):
        zope.component.getUtility(IMessageSource).send(msg)


def test_testing__Browser__message__1(fake_session, browser):
    """It is an empty list if there are no flash messages."""
    browser.login('mgr')
    browser.open('http://localhost')
    assert [] == browser.message


def test_testing__Browser__message__2(fake_session, browser):
    """It is a string if there is exactly one flash message."""
    send_msg('foo')
    browser.login('mgr')
    browser.handleErrors = False
    browser.open('http://localhost')
    assert 'foo' == browser.message


def test_testing__Browser__message__3(fake_session, browser):
    """It is a list of strings if there is more than one flash message."""
    send_msg('foo')
    send_msg('blah')
    browser.login('mgr')
    browser.open('http://localhost')
    assert ['foo', 'blah'] == browser.message

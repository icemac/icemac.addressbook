# -*- coding: utf-8 -*-
from icemac.addressbook.testing import pyTestAddressBookFixture, site
from icemac.addressbook.testing import pyTestEmptyZodbFixture, DateTimeClass
from icemac.addressbook.testing import pyTestStackDemoStorage
import gocept.country.db
import icemac.addressbook
import icemac.addressbook.browser.interfaces
import icemac.addressbook.file.interfaces
import icemac.addressbook.interfaces
import icemac.addressbook.principals.principals
import icemac.addressbook.startup
import icemac.addressbook.testing
import icemac.addressbook.utils
import pytest
import transaction
import zope.app.wsgi.testlayer
import zope.browserpage.metaconfigure
import zope.component.hooks
import zope.event
import zope.principalregistry.principalregistry
import zope.processlifetime
import zope.publisher.browser
import zope.testbrowser.wsgi

pytest_plugins = 'icemac.addressbook.fixtures'


# Fixtures to set-up infrastructure which are usable in tests:

@pytest.yield_fixture(scope='function')
def empty_zodb(zodbS):
    """Get the address book from the right demo storage."""
    for connection in pyTestStackDemoStorage(zodbS, 'EmptyZODB'):
        yield connection


@pytest.yield_fixture(scope='function')
def address_book(addressBookConnectionF):
    """Get the address book as site."""
    for address_book in site(addressBookConnectionF):
        yield address_book


@pytest.yield_fixture(scope='function')
def translated_address_book(translationZcmlF):
    """Get the address book as site for translation tests."""
    for zodb in pyTestEmptyZodbFixture():
        for zodb in pyTestAddressBookFixture(zodb, 'TranslatedAddressBook'):
            for conn in pyTestStackDemoStorage(zodb, 'TranslatedAddressBook2'):
                for address_book in site(conn):
                    yield address_book


@pytest.yield_fixture(scope='function')
def person_data(personDataS):
    """Provide predefined person data, see `personDataS`."""
    for connection in icemac.addressbook.conftest.pyTestStackDemoStorage(
            personDataS.zodb, 'PersonFunction'):
        for addressbook in site(connection):
            yield addressbook


@pytest.fixture(scope='function')
def browser_request():
    """Provide a browser request which is set as global request."""
    request = zope.publisher.browser.TestRequest()
    zope.interface.alsoProvides(
        request, icemac.addressbook.browser.interfaces.IAddressBookLayer)
    old_request = zope.globalrequest.getRequest()
    zope.globalrequest.setRequest(request)
    yield request
    zope.globalrequest.setRequest(old_request)


@pytest.fixture(scope='function')
def browser(browserWsgiAppS):
    """Fixture for testing with zope.testbrowser."""
    assert icemac.addressbook.testing.CURRENT_CONNECTION is not None, \
        "The `browser` fixture needs a database fixture like `address_book`."
    return icemac.addressbook.testing.Browser(wsgi_app=browserWsgiAppS)


@pytest.fixture(scope='function')
def browser2(browserWsgiAppS):
    """Fixture for testing with a second zope.testbrowser."""
    return icemac.addressbook.testing.Browser(wsgi_app=browserWsgiAppS)


@pytest.fixture(scope='function')
def browser3(browserWsgiAppS):
    """Fixture for testing with a third zope.testbrowser."""
    return icemac.addressbook.testing.Browser(wsgi_app=browserWsgiAppS)


# Fixtures to help asserting

@pytest.fixture(scope='function')
def sitemenu(browser):
    """Helper fixture to test the selections in the site menu.

    USABLE IN TESTS.

    """
    return icemac.addressbook.testing.SiteMenu


@pytest.fixture(scope='function')
def assert_address_book(address_book):
    """Fixture returning an object providing a custom address book asserts."""
    return icemac.addressbook.testing.AddressBookAssertions(address_book)


# generally usable helper fixtures:


@pytest.fixture(scope='session')
def DateTime():
    """Fixture to ease handling of datetime objects."""
    return DateTimeClass()


# Infrastructure fixtures

@pytest.yield_fixture(scope='session')
def zcmlS():
    """Load ZCML on session scope."""
    layer = icemac.addressbook.testing.SecondaryZCMLLayer(
        'AddressBook', __name__, icemac.addressbook, [])
    layer.setUp()
    yield layer
    layer.tearDown()
    # Needed so another ZCML layer can be run.
    zope.browserpage.metaconfigure.clear()
    zope.principalregistry.principalregistry.principalRegistry._clear()


@pytest.yield_fixture(scope='session')
def zodbS(zcmlS):
    """Create an empty test ZODB."""
    for zodb in icemac.addressbook.testing.pyTestEmptyZodbFixture():
        yield zodb


@pytest.yield_fixture(scope='session')
def addressBookS(zodbS):
    """Create an address book for the session."""
    for zodb in pyTestAddressBookFixture(zodbS, 'AddressBookS'):
        yield zodb


@pytest.yield_fixture(scope='function')
def addressBookConnectionF(addressBookS):
    """Get the connection to the right demo storage."""
    for connection in pyTestStackDemoStorage(addressBookS, 'AddressBookF'):
        yield connection


@pytest.yield_fixture(scope='function')
def translationZcmlF(zcmlS):
    """Load ZCML including locales packages on session scope."""
    layer = icemac.addressbook.testing.SecondaryZCMLLayer(
        'TranslatedAddressBook', __name__, icemac.addressbook, [zcmlS],
        filename='translationtesting.zcml')
    layer.setUp()
    yield layer
    layer.tearDown()


@pytest.yield_fixture(scope='session')
def personDataS(
        addressBookS, FullPersonFactory, PostalAddressFactory, KeywordFactory,
        PhoneNumberFactory, EMailAddressFactory, HomepageAddressFactory):
    """Create base data used in person tests."""
    for connection in icemac.addressbook.conftest.pyTestStackDemoStorage(
            addressBookS, 'PersonDataSession'):
        for address_book in icemac.addressbook.conftest.site(connection):
            _create_person(
                address_book, FullPersonFactory, PostalAddressFactory,
                KeywordFactory, PhoneNumberFactory, EMailAddressFactory,
                HomepageAddressFactory)
            yield connection


# Helper functions and classes


def _create_person(
        address_book, FullPersonFactory, PostalAddressFactory, KeywordFactory,
        PhoneNumberFactory, EMailAddressFactory, HomepageAddressFactory, **kw):
    """Create a person, usable in tests."""
    KeywordFactory(address_book, u'friend')

    person = FullPersonFactory(
        address_book, u'Tester', first_name=u'Petra',
        keywords=[u'family', u'church'],
        postal__address_prefix=u'c/o Mama', postal__zip=u'88888',
        postal__street=u'Demoweg 23', postal__city=u'Testhausen',
        postal__country=gocept.country.db.Country('AT'),
        phone__number=u'+4901767654321', email__email=u'petra@example.com',
        homepage__url=b'http://petra.example.com', **kw)
    PostalAddressFactory(
        person, address_prefix=u'RST-Software',
        street=u'Forsterstraße 302a', zip=u'98344', city=u'Erfurt')
    PhoneNumberFactory(person, number=u'+4901761234567')
    EMailAddressFactory(person, email=u'pt@rst.example.edu')
    HomepageAddressFactory(person, url='http://www.rst.example.edu')
    transaction.commit()

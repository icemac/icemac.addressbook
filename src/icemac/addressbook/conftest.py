# -*- coding: utf-8 -*-
from icemac.addressbook.testing import pyTestAddressBookFixture, site
from icemac.addressbook.testing import pyTestEmptyZodbFixture, DateTimeClass
from icemac.addressbook.testing import pyTestStackDemoStorage
import gocept.httpserverlayer.wsgi
import gocept.selenium
import gocept.selenium.wd_selenese
import icemac.addressbook
import icemac.addressbook.file.interfaces
import icemac.addressbook.interfaces
import icemac.addressbook.principals.principals
import icemac.addressbook.startup
import icemac.addressbook.testing
import icemac.addressbook.utils
import mock
import os
import os.path
import pytest
import tempfile
import transaction
import zope.app.wsgi.testlayer
import zope.browserpage.metaconfigure
import zope.component.hooks
import zope.event
import zope.i18n
import zope.principalregistry.principalregistry
import zope.processlifetime
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


def interpolate_insted_of_translate(self, msgid, mapping=None, *args, **kw):
    """Use interpolation instead of translation."""
    return zope.i18n.interpolate(msgid, mapping)


@pytest.yield_fixture(scope='function')
def webdriver(webdriverS, httpServerS):
    """Fixture to run tests using Webdriver."""
    assert icemac.addressbook.testing.CURRENT_CONNECTION is not None, \
        "The `webdriver` fixture needs a database fixture like `address_book`."
    timeout = int(os.environ.get('GOCEPT_SELENIUM_TIMEOUT', 10))
    webdriver = icemac.addressbook.testing.Webdriver(
        gocept.selenium.wd_selenese.Selenese(
            webdriverS, httpServerS, timeout))
    # Allow any language setting in the Webdriver browser by falling back to
    # interpolation instead of translation:
    translate = 'zope.i18n.translationdomain.TranslationDomain.translate'
    getPreferredLanguages = (
        'zope.publisher.browser.BrowserLanguages.getPreferredLanguages')
    with mock.patch(translate, new=interpolate_insted_of_translate), \
            mock.patch(getPreferredLanguages, return_value=['en-us', 'en']):
        yield webdriver


@pytest.yield_fixture(scope='function')
def tmpfile():
    """Fixture to create a temporary file with a defined content and suffix.

    Returns a callable to create the file which returns a tuple of file handle
    and file name.

    """
    filename = None
    fhr = None

    def tmpfile(content, suffix):
        fd, filename = tempfile.mkstemp(suffix=suffix)
        # It does not seem to be possible to use os.fdopen with 'rw' -- it
        # leads to "[Errno 9] Bad file descriptor"
        with os.fdopen(fd, 'w') as fhw:
            fhw.write(content)
        fhr = file(filename, 'r')
        return fhr, os.path.basename(filename)
    yield tmpfile
    if fhr is not None:
        fhr.close()
        os.unlink(filename)


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


# Factory fixtures to create objects:

@pytest.fixture(scope='function')
def AddressBookFactory(addressBookConnectionF):
    """Create an address book in the root folder."""
    def create_addressbook(name, title=None):
        return icemac.addressbook.testing.create_addressbook(
            addressBookConnectionF.rootFolder, name, title)
    return create_addressbook

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

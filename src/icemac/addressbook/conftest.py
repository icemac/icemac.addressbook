# -*- coding: utf-8 -*-
from icemac.addressbook.principals.sources import role_source
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
import plone.testing.zodb
import pytest
import tempfile
import transaction
import zope.app.wsgi.testlayer
import zope.component.hooks
import zope.event
import zope.i18n
import zope.processlifetime
import zope.testbrowser.wsgi


CURRENT_CONNECTION = None


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
    assert CURRENT_CONNECTION is not None, \
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
    assert CURRENT_CONNECTION is not None, \
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
    class SiteMenu(object):
        """Helper class to test selections in the site menu."""

        def __init__(self, browser, menu_item_index, menu_item_title,
                     menu_item_URL):
            """Parameters:

            browser ... return value of the ``browser`` fixture.
            menu_item_index ... zero-based index of the position of the item in
                                 the menu
            menu_item_title ... title of the menu item
            menu_item_URL ... URL the menu item should point to

            """
            self.browser = browser
            self.menu_item_index = menu_item_index
            self.menu_item_title = menu_item_title
            self.menu_item_URL = menu_item_URL

        def item_selected(self, url):
            self.browser.open(url)
            return bool(
                self.browser.etree.xpath(self._xpath)[0].attrib.get('class'))

        def assert_correct_menu_item_is_tested(self):
            self.browser.open(self.menu_item_URL)
            assert self.menu_item_title == self.browser.etree.xpath(
                '%s/a/span' % self._xpath)[0].text

        @property
        def _xpath(self):
            # xpath is one based!
            return '//ul[@id="main-menu"]/li[%s]' % (self.menu_item_index + 1)

    return SiteMenu


@pytest.fixture(scope='function')
def assert_address_book(address_book):
    """Fixture returning an object providing a custom address book asserts."""
    class Assertions:
        """Assertions helpful to check automatic installation routines."""

        def __init__(self, address_book):
            self.address_book = address_book

        def has_local_utility(self, iface, name=''):
            """Assert that there is a local utility for the given interface."""
            util = zope.component.queryUtility(
                iface, context=self.address_book, name=name)
            assert util is not None

        def has_attribute(self, attribute, iface, name=''):
            """Assert the address book has an attribute provided as utility."""
            assert iface.providedBy(getattr(self.address_book, attribute))
            self.has_local_utility(iface, name)

    return Assertions(address_book)


# Fixtures to create objects:

@pytest.fixture(scope='function')
def AddressBookFactory(addressBookConnectionF):
    """Create an address book in the root folder."""
    def create_addressbook(name, title=None):
        return icemac.addressbook.testing.create_addressbook(
            addressBookConnectionF.rootFolder, name, title)
    return create_addressbook


@pytest.fixture(scope='session')
def FieldFactory():
    """Create a user defined field in the address book.

    type ... see values of .sources.FieldTypeSource

    To create values for a Choice field use: values=<list of values>
    """
    def create(address_book, iface, type, title, **kw):
        with zope.component.hooks.site(address_book):
            field = icemac.addressbook.utils.create_obj(
                icemac.addressbook.entities.Field, type=type, title=title,
                **kw)
            entity = icemac.addressbook.interfaces.IEntity(iface)
            return entity.getRawField(entity.addField(field))
    return create


@pytest.fixture(scope='session')
def KeywordFactory():
    """Create a keyword in the address book."""
    def create_keyword(address_book, title, **kw):
        return icemac.addressbook.testing.create(
            address_book, address_book.keywords,
            icemac.addressbook.interfaces.IKeyword, title=title, **kw)
    return create_keyword


@pytest.fixture(scope='session')
def PersonFactory(KeywordFactory):
    """Create a person in the address book."""
    def create_person(address_book, last_name, keywords=[], **kw):
        keywords_set = set()
        keywords_util = zope.component.getUtility(
            icemac.addressbook.interfaces.IKeywords)
        for candidate in keywords:
            if icemac.addressbook.interfaces.IKeyword.providedBy(candidate):
                keyword = candidate
            else:
                keyword = keywords_util.get_keyword_by_title(candidate)
                if keyword is None:
                    keyword = KeywordFactory(address_book, candidate)
            keywords_set.add(keyword)
        return icemac.addressbook.testing.create(
            address_book, address_book, icemac.addressbook.interfaces.IPerson,
            last_name=last_name, keywords=keywords_set, **kw)
    return create_person


@pytest.fixture(scope='session')
def FullPersonFactory(
        PersonFactory, PostalAddressFactory, EMailAddressFactory,
        PhoneNumberFactory, HomepageAddressFactory, KeywordFactory):
    """Create a fully defined person in the address book usable in browser.

    Use <entity_name>__<attrib> to write to numbers and addresses.
    Possible entity names: 'email', 'phone', 'postal', 'homepage'

    The `keywords` parameter accepts an iterable of either keyword objects or
    keyword titles. Not existing keywords are created.

    """
    def create_full_person(address_book, last_name, **kw):
        by_entity = {}
        for key, value in kw.items():
            entity, _, attrib = key.partition('__')
            if not attrib:
                # default to 'person' for not prefixed keys
                attrib = entity
                entity = 'person'
            by_entity.setdefault(entity, {})[attrib] = value

        person = PersonFactory(
            address_book, last_name=last_name, **by_entity.get('person', {}))
        PostalAddressFactory(
            person, set_as_default=True, **by_entity.get('postal', {}))
        EMailAddressFactory(
            person, set_as_default=True, **by_entity.get('email', {}))
        PhoneNumberFactory(
            person, set_as_default=True, **by_entity.get('phone', {}))
        HomepageAddressFactory(
            person, set_as_default=True, **by_entity.get('homepage', {}))
        return person
    return create_full_person


@pytest.fixture(scope='session')
def PostalAddressFactory():
    """Create a postal address for a person in the address book."""
    def create_postal_address(
            person, set_as_default=False, **kw):
        return icemac.addressbook.testing.create(
            person.__parent__, person,
            icemac.addressbook.interfaces.IPostalAddress,
            set_as_default=set_as_default, **kw)
    return create_postal_address


@pytest.fixture(scope='session')
def EMailAddressFactory():
    """Create a e-mail address for a person in the address book."""
    def create_email_address(person, email=None, set_as_default=False, **kw):
        return icemac.addressbook.testing.create(
            person.__parent__, person,
            icemac.addressbook.interfaces.IEMailAddress,
            email=email, set_as_default=set_as_default, **kw)
    return create_email_address


@pytest.fixture(scope='session')
def PhoneNumberFactory():
    """Create a phone number for a person in the address book."""
    def create_phone_number(person, set_as_default=False, **kw):
        return icemac.addressbook.testing.create(
            person.__parent__, person,
            icemac.addressbook.interfaces.IPhoneNumber,
            set_as_default=set_as_default, **kw)
    return create_phone_number


@pytest.fixture(scope='session')
def HomepageAddressFactory():
    """Create a home page address for a person in the address book."""
    def create_home_page_address(person, set_as_default=False, **kw):
        return icemac.addressbook.testing.create(
            person.__parent__, person,
            icemac.addressbook.interfaces.IHomePageAddress,
            set_as_default=set_as_default, **kw)
    return create_home_page_address


@pytest.fixture(scope='session')
def FileFactory():
    """Create a file for a person in the address book."""
    def create_file(person, filename, **kw):
        return icemac.addressbook.testing.create(
            person.__parent__, person,
            icemac.addressbook.file.interfaces.IFile, name=filename, **kw)
    return create_file


@pytest.fixture(scope='session')
def UserFactory(FullPersonFactory):
    """Create a user in the address book.

    roles ... list of role titles (!)
    """
    def create_user(
            address_book, first_name, last_name, email, password, roles,
            keywords=[], **kw):
        person = FullPersonFactory(
            address_book, first_name=first_name, last_name=last_name,
            email__email=email, keywords=keywords)
        role_factory = role_source.factory
        role_values = role_factory.getValues()
        selected_roles = []
        for role_title in roles:
            for candidate in role_values:
                if role_factory.getTitle(candidate) == role_title:
                    selected_roles.append(candidate)
                    break
            else:
                raise LookupError(
                    'Role title {!r} unknown.'.format(role_title))
        # Cannot use icemac.addressbook.testing() here because `Principal` is
        # not an entity.
        name = icemac.addressbook.utils.create_and_add(
            address_book.principals,
            icemac.addressbook.principals.principals.Principal,
            person=person, password=password, roles=selected_roles)
        return address_book.principals[name]
    return create_user


# Infrastructure fixtures

@pytest.yield_fixture(scope='session')
def zcmlS():
    """Load ZCML on session scope."""
    layer = icemac.addressbook.testing.SecondaryZCMLLayer(
        'AddressBook', __name__, icemac.addressbook, [])
    layer.setUp()
    yield layer
    layer.tearDown()


@pytest.yield_fixture(scope='session')
def zodbS(zcmlS):
    """Create an empty test ZODB."""
    for zodb in pyTestEmptyZodbFixture():
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


@pytest.fixture(scope='session')
def wsgiAppS():
    """Create a WSGI application. for the current package."""
    zope_appl = icemac.addressbook.startup.zope_application_factory()
    zope_appl.requestFactory = TestHTTPPublicationRequestFactory()
    return icemac.addressbook.startup.application_factory(
        zope_application=zope_appl)


def getRootFolder():
    """`TransactionMiddleware` expects a callable to get the root folder."""
    return CURRENT_CONNECTION.rootFolder


@pytest.fixture(scope='session')
def browserWsgiAppS(wsgiAppS):
    """WSGI application layered with some middlewares for testbrowser."""
    return zope.testbrowser.wsgi.AuthorizationMiddleware(
        zope.app.wsgi.testlayer.TransactionMiddleware(
            getRootFolder, wsgiAppS))


@pytest.yield_fixture(scope='session')
def httpServerS(wsgiAppS):
    """Create a HTTPServer for the WSGI app."""
    server = gocept.httpserverlayer.wsgi.Layer()
    server.wsgi_app = wsgiAppS
    server.setUp()
    server.url = 'http://{}'.format(server['http_address'])
    yield server['http_address']
    server.tearDown()


@pytest.yield_fixture(scope='session')
def webdriverS(httpServerS):
    """Open a browser for webriver tests."""
    layer = gocept.selenium.WebdriverLayer(name='WebdriverLayer')
    layer['http_address'] = httpServerS
    layer.setUp()
    yield layer['seleniumrc']
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


def pyTestEmptyZodbFixture():
    """Create an empty ZODB prepared to create an address book inside.

    Yields the zodb object.

    Prepared to be usable with a ``pytest.yield_fixture()``.

    """
    layer = plone.testing.zodb.EmptyZODB()
    layer.setUp()
    zodb = layer['zodbDB']
    zope.event.notify(zope.processlifetime.DatabaseOpened(zodb))
    transaction.commit()
    yield zodb
    layer.tearDown()


def pyTestAddressBookFixture(zodb, name):
    """Create an address book in the ZODB.

    Expects an empty ZODB as created by pyTestEmptyZodbFixture() and a name
    for the demo storage layer.

    Yields the zodb object.

    Prepared to be usable with a ``pytest.yield_fixture()``.

    """
    for connection in pyTestStackDemoStorage(zodb, name):
        icemac.addressbook.testing.create_addressbook(
            connection.rootFolder, name='ab', title=u'test addressbook')
        transaction.commit()
        yield connection.zodb


def pyTestStackDemoStorage(zodb, name):
    """Put a demo storage on top of ``zodb`` and yield the connection tuple.

    Prepared to be usable with a ``pytest.yield_fixture()``.

    """
    global CURRENT_CONNECTION
    storage = plone.testing.zodb.stackDemoStorage(zodb, name=name)
    connection = icemac.addressbook.testing.createZODBConnection(storage)
    transaction.begin()
    CURRENT_CONNECTION = connection
    yield connection
    storage.close()
    transaction.abort()
    connection.connection.close()
    CURRENT_CONNECTION = None


class NonCachingPublicationCache(object):
    """Replacement to prevent caching of ZODB connections."""

    def get(self, key):
        return None

    def __setitem__(self, key, value):
        """Do not cache!"""
        pass


class TestHTTPPublicationRequestFactory(
        zope.app.publication.httpfactory.HTTPPublicationRequestFactory):
    """RequestFactory which uses the global `CURRENT_CONNECTION`."""

    def __init__(self):
        super(TestHTTPPublicationRequestFactory, self).__init__(None)
        self._publication_cache = NonCachingPublicationCache()

    @property
    def _db(self):
        return CURRENT_CONNECTION.zodb

    @_db.setter
    def _db(self, value):
        """Ignoring `value` because the global one should always be used."""


def site(connection):
    """Get the address book from the connection and set it as site.

    Usable in a `yield_fixture`.
    Resets the site to its previous value at exit.

    """
    addressbook = connection.rootFolder['ab']
    with zope.component.hooks.site(addressbook):
        yield addressbook


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

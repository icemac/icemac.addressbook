# -*- coding: utf-8 -*-
from icemac.addressbook.principals.sources import role_source
from icemac.addressbook.testing import TestHTTPPublicationRequestFactory
from icemac.addressbook.testing import getRootFolder
from icemac.addressbook.testing import interpolate_insted_of_translate
import gocept.httpserverlayer.wsgi
import icemac.addressbook
import icemac.addressbook.browser.interfaces
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
import selenium.webdriver
import tempfile
import zope.app.wsgi.testlayer
import zope.browserpage.metaconfigure
import zope.component.hooks
import zope.event
import zope.i18n
import zope.principalregistry.principalregistry
import zope.processlifetime
import zope.publisher.browser
import zope.testbrowser.wsgi

# Integrate these fixtures using:
# pytest_plugins = 'icemac.addressbook.fixtures'
# in your `conftest.py`


# Fixtures ready to use in tests:


@pytest.yield_fixture(scope='function')
def webdriver(webdriverS, httpServerS):  # pragma: no cover (webdriver)
    """Fixture to run tests using Webdriver."""
    assert icemac.addressbook.testing.CURRENT_CONNECTION is not None, \
        "The `webdriver` fixture needs a database fixture like `address_book`."
    webdriver = icemac.addressbook.testing.Webdriver(webdriverS, httpServerS)
    # Allow any language setting in the Webdriver browser by falling back to
    # interpolation instead of translation:
    translate = 'zope.i18n.translationdomain.TranslationDomain.translate'
    getPreferredLanguages = (
        'zope.publisher.browser.BrowserLanguages.getPreferredLanguages')
    message_display_timeout = (
        'icemac.addressbook.browser.messages.messages.'
        'MessagesContentProvider.message_display_timeout')
    with mock.patch(translate, new=interpolate_insted_of_translate), \
            mock.patch(getPreferredLanguages, return_value=['en-us', 'en']), \
            mock.patch(message_display_timeout,
                       new_callable=mock.PropertyMock, return_value=300):
        yield webdriver


# Factory fixtures to create objects:


@pytest.fixture('function')
def RequestFactory():
    """Get a request object on the right skin layer."""
    def get_request(**kw):
        return zope.publisher.browser.TestRequest(
            skin=icemac.addressbook.browser.interfaces.IAddressBookLayer,
            **kw)
    return get_request


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
        known_roles = []
        for role_title in roles:
            for candidate in role_values:
                known_role = role_factory.getTitle(candidate)
                known_roles.append(known_role)
                if known_role == role_title:
                    selected_roles.append(candidate)
                    break
            else:
                raise LookupError(
                    'Role title {!r} unknown. Known ones: {!r}'.format(
                        role_title, known_roles))
        # Cannot use icemac.addressbook.testing.create() here because
        # `Principal` is not an entity.
        name = icemac.addressbook.utils.create_and_add(
            address_book.principals,
            icemac.addressbook.principals.principals.Principal,
            person=person, password=password, roles=selected_roles)
        return address_book.principals[name]
    return create_user


@pytest.fixture(scope='function')
def AddressBookFactory(addressBookConnectionF):
    """Create an address book in the root folder."""
    def create_addressbook(name, title=None):
        return icemac.addressbook.testing.create_addressbook(
            addressBookConnectionF.rootFolder, name, title)
    return create_addressbook


# generally usable helper fixtures:


@pytest.yield_fixture('function')
def TimeZonePrefFactory():
    """Factory to set the time zone in the preferences.

    Usage example:  TimeZonePrefFactory('Europe/Berlin')
    """
    patchers = []

    def set_time_zone_pref(time_zone_name):
        patcher = mock.patch(
            'icemac.addressbook.preferences.utils.get_time_zone_name',
            return_value=time_zone_name)
        patcher.start()
        patchers.append(patcher)
    yield set_time_zone_pref
    while patchers:
        patchers.pop().stop()


@pytest.yield_fixture(scope='function')
def tmpfile():
    """Fixture to create a temporary file with a defined content and suffix.

    Returns a callable to create the file which returns a tuple of file handle
    and file name.

    """
    data = {'filename': None, 'fhr': None}

    def tmpfile(content, suffix, _data=data):
        fd, filename = tempfile.mkstemp(suffix=suffix)
        # It does not seem to be possible to use os.fdopen with 'rw' -- it
        # leads to "[Errno 9] Bad file descriptor"
        with os.fdopen(fd, 'w') as fhw:
            fhw.write(content)
        data['fhr'] = open(filename, 'r')
        data['filename'] = filename
        return data['fhr'], os.path.basename(filename)
    yield tmpfile
    assert data['fhr'] is not None, \
        "You required this fixture but the test failed before using it."
    data['fhr'].close()
    os.unlink(data['filename'])


# Infrastructure fixtures


@pytest.fixture(scope='session')
def wsgiAppS():
    """Create a WSGI application. for the current package."""
    zope_appl = icemac.addressbook.startup.zope_application_factory()
    zope_appl.requestFactory = TestHTTPPublicationRequestFactory()
    return icemac.addressbook.startup.application_factory(
        zope_application=zope_appl)


@pytest.fixture(scope='session')
def browserWsgiAppS(wsgiAppS):
    """WSGI application layered with some middlewares for testbrowser."""
    return zope.testbrowser.wsgi.AuthorizationMiddleware(
        zope.app.wsgi.testlayer.TransactionMiddleware(
            getRootFolder, wsgiAppS))


@pytest.yield_fixture(scope='session')
def httpServerS(wsgiAppS):  # pragma: no cover (webriver)
    """Create a HTTPServer for the WSGI app."""
    server = gocept.httpserverlayer.wsgi.Layer()
    server.wsgi_app = wsgiAppS
    server.setUp()
    server.url = 'http://{}'.format(server['http_address'])
    yield server['http_address']
    server.tearDown()


@pytest.yield_fixture(scope='session')
def webdriverS(httpServerS):  # pragma: no cover (webdriver)
    """Open a browser for webriver tests."""
    if os.environ.get('SELENIUM_FIREFOX', False):
        options = selenium.webdriver.FirefoxOptions()
        options.add_argument('window-size=1200x800')
        if not os.environ.get('NOT_HEADLESS', False):
            options.headless = True
        driver = selenium.webdriver.Firefox(options=options)
    else:
        options = selenium.webdriver.ChromeOptions()
        options.add_argument('window-size=1200x800')
        if not os.environ.get('NOT_HEADLESS', False):
            options.add_argument('headless')
        driver = selenium.webdriver.Chrome(options=options)

    timeout = int(os.environ.get('GOCEPT_SELENIUM_TIMEOUT', 10))
    driver.implicitly_wait(timeout)  # in seconds
    try:
        yield driver
    finally:
        driver.quit()

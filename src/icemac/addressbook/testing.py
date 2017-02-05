# -*- coding: utf-8 -*-
import collections
import datetime
import gocept.jslint
import icemac.addressbook.addressbook
import icemac.addressbook.interfaces
import icemac.addressbook.person
import icemac.addressbook.startup
import icemac.addressbook.utils
import lxml.etree
import os
import plone.testing
import plone.testing.zca
import plone.testing.zodb
import pytest
import pytz
import transaction
import webtest.forms
import z3c.etestbrowser.wsgi
import zope.app.publication.zopepublication
import zope.app.wsgi.testlayer
import zope.component
import zope.component.hooks
import zope.i18n
import zope.testbrowser.browser
import zope.testbrowser.interfaces
import zope.testbrowser.wsgi


CURRENT_CONNECTION = None
ZODBConnection = collections.namedtuple(
    'ZODBConnection', ['connection', 'rootFolder', 'zodb'])


def createZODBConnection(zodbDB):
    """Create an open ZODB connection."""
    connection = zodbDB.open()
    rootFolder = connection.root()[
        zope.app.publication.zopepublication.ZopePublication.root_name]
    return ZODBConnection(connection, rootFolder, zodbDB)


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


def site(connection):
    """Get the address book from the connection and set it as site.

    Usable in a `yield_fixture`.
    Resets the site to its previous value at exit.

    """
    addressbook = connection.rootFolder['ab']
    with zope.component.hooks.site(addressbook):
        yield addressbook


# Layer factories


def SecondaryZCMLLayer(
        name, module, package, bases=(), filename="ftesting.zcml"):
    """Factory to create a new ZCML test layer above an existing one."""
    return plone.testing.zca.ZCMLSandbox(
        name="%sZCML" % name, bases=bases, filename=filename,
        module=module, package=package)


# Test cases

class JSLintTest(gocept.jslint.TestCase):
    """Base test class for JS lint tests."""

    jshint_command = os.environ.get('JSHINT_COMMAND', '/bin/false')
    options = (gocept.jslint.TestCase.options + (
               'evil',
               'eqnull',
               'multistr',
               'sub',
               'undef',
               'browser',
               'jquery',
               'devel'
               ))


# List of users those passwords are not equal to the login name:
USERNAME_PASSWORD_MAP = dict(
    mgr='mgrpw',
    globalmgr='globalmgrpw'
)


class Browser(z3c.etestbrowser.wsgi.ExtendedTestBrowser):
    """Enriched test browser."""

    ROOT_URL = 'http://localhost'
    # The login URL starts with this string:
    LOGIN_BASE_URL = 'http://localhost/ab/@@loginForm.html?camefrom=http'

    ADDRESS_BOOK_DEFAULT_URL = 'http://localhost/ab'
    ADDRESS_BOOK_WELCOME_URL = 'http://localhost/ab/@@welcome.html'
    ADDRESS_BOOK_EDIT_URL = 'http://localhost/ab/@@edit-address_book.html'
    ADDRESS_BOOK_DELETE_PERSONS_URL = (
        'http://localhost/ab/@@delete-address_book-content.html')
    ADDRESS_BOOK_DELETE_URL = 'http://localhost/ab/@@delete-address_book.html'

    MASTER_DATA_URL = 'http://localhost/ab/@@masterdata.html'

    ENTITIES_EDIT_URL = 'http://localhost/ab/++attribute++entities'
    ENTITY_PERSON_LIST_FIELDS_URL = (
        'http://localhost/ab/++attribute++entities/'
        'icemac.addressbook.person.Person')
    ENTITY_PERSON_ADD_FIELD_URL = (
        'http://localhost/ab/++attribute++entities/'
        'icemac.addressbook.person.Person/@@addField.html')
    ENTITIY_PERSON_EDIT_FIELD_URL = (
        'http://localhost/ab/++attribute++entities/'
        'icemac.addressbook.person.Person/Field-1')
    ENTITIY_PERSON_DELETE_FIELD_URL = (
        'http://localhost/ab/++attribute++entities/'
        'icemac.addressbook.person.Person/Field-1/@@delete.html')

    KEYWORDS_LIST_URL = 'http://localhost/ab/++attribute++keywords'
    KEYWORD_ADD_URL = (
        'http://localhost/ab/++attribute++keywords/@@addKeyword.html')
    KEYWORD_EDIT_URL = 'http://localhost/ab/++attribute++keywords/Keyword'
    KEYWORD_DELETE_URL = (
        'http://localhost/ab/++attribute++keywords/Keyword/@@delete.html')

    PERSON_ADD_URL = 'http://localhost/ab/@@addPerson.html'
    PERSON_CLONE_URL = 'http://localhost/ab/Person/@@clone.html'
    PERSON_EDIT_URL = 'http://localhost/ab/Person'
    PERSONS_LIST_URL = 'http://localhost/ab/@@person-list.html'
    PERSON_DELETE_URL = 'http://localhost/ab/Person/@@delete_person.html'
    PERSON_DELETE_ENTRY_URL = (
        'http://localhost/ab/Person/@@delete_entry.html')
    PERSON_EXPORT_URL = 'http://localhost/ab/Person/@@export.html'

    POSTAL_ADDRESS_DELETE_URL = (
        'http://localhost/ab/Person/PostalAddress-2/@@delete.html')
    PHONE_NUMBER_DELETE_URL = (
        'http://localhost/ab/Person/PhoneNumber-2/@@delete.html')
    EMAIL_ADDRESS_DELETE_URL = (
        'http://localhost/ab/Person/EMailAddress-2/@@delete.html')
    HOMEPAGE_ADDRESS_DELETE_URL = (
        'http://localhost/ab/Person/HomePageAddress-2/@@delete.html')

    FILE_ADD_URL = 'http://localhost/ab/Person/@@addFile.html'
    FILE_DELETE_URL = 'http://localhost/ab/Person/File/@@delete.html'
    FILE_DOWNLOAD_URL = 'http://localhost/ab/Person/File/download.html'

    PRINCIPALS_LIST_URL = 'http://localhost/ab/++attribute++principals'
    PRINCIPAL_ADD_URL = (
        'http://localhost/ab/++attribute++principals/@@addPrincipal.html')
    PRINCIPAL_EDIT_URL = 'http://localhost/ab/++attribute++principals/2'
    PRINCIPAL_EDIT_URL_1 = 'http://localhost/ab/++attribute++principals/1'
    PRINCIPAL_DELETE_URL = (
        'http://localhost/ab/++attribute++principals/2/@@delete_user.html')
    PRINCIPAL_DELETE_URL_1 = (
        'http://localhost/ab/++attribute++principals/1/@@delete_user.html')

    SEARCH_URL = 'http://localhost/ab/@@search.html'
    SEARCH_BY_NAME_URL = 'http://localhost/ab/@@name_search.html'
    SEARCH_BY_KEYWORD_URL = 'http://localhost/ab/@@multi_keyword.html'
    SEARCH_MULTI_UPDATE_URL = 'http://localhost/ab/@@multi-update'
    SEARCH_MULTI_UPDATE_CHOOSE_FIELD_URL = (
        'http://localhost/ab/multi-update/chooseField')
    SEARCH_MULTI_UPDATE_ENTER_VALUE_URL = (
        'http://localhost/ab/multi-update/enterValue')
    SEARCH_MULTI_UPDATE_CHECK_RESULT_URL = (
        'http://localhost/ab/multi-update/checkResult')
    SEARCH_MULTI_UPDATE_COMPLETE_URL = (
        'http://localhost/ab/@@multi-update-completed')
    SEARCH_DELETE_URL = 'http://localhost/ab/@@delete_persons.html'

    PREFS_URL = 'http://localhost/ab/++preferences++/ab'
    PREFS_TIMEZONE_URL = (
        'http://localhost/ab/++preferences++/ab.timeZone/@@index.html')

    INSPECTOR_VIEW_URL = PERSONS_LIST_URL + '/@@inspector'
    INSPECTOR_OBJECT_URL = KEYWORDS_LIST_URL + '/@@inspector'
    INSPECTOR_ROOT_OBJECT_URL = ROOT_URL + '/@@inspector'

    def login(self, username, password=None):
        """Login a user using basic auth."""
        password = USERNAME_PASSWORD_MAP.get(username, username)
        self.addHeader(
            'Authorization', 'Basic {username}:{password}'.format(
                username=username, password=password))
        return self

    def formlogin(self, username, password, use_current_url=False):
        """Login using the login form."""
        if not use_current_url:
            self.open(self.ADDRESS_BOOK_DEFAULT_URL)
        self.getControl('User Name').value = username
        self.getControl('Password').value = password
        self.getControl('Log in').click()
        assert 'You have been logged-in successfully.' == self.message
        return self

    def lang(self, lang):
        """Set the language for the browser."""
        self.addHeader('Accept-Language', lang)

    def open(self, url):
        super(Browser, self).open(url)
        return self

    @property
    def contents_without_whitespace(self):
        """Browser contents but with removed whitespace."""
        return self.contents.replace(' ', '').replace('\n', '')

    def etree_to_list(self, etree):
        """"Convert an etree into a list (lines without leading whitespace.)"""
        return [x.strip()
                for x in lxml.etree.tostring(etree).split('\n')
                if x.strip()]

    @property
    def message(self):
        """Return the info messages displayed in browser.

        Returns string when there is exactly one message, list otherwise.
        """
        messages = [x.text
                    for x in self.etree.xpath(
                        '//div[@id="info-messages"]/ul/li')]
        if len(messages) == 1:
            return messages[0]
        return messages

    def keyword_search(self, keyword, apply=None):
        """Search for a keyword via keyword-search.

        If `apply` is not `None` select the value from the dropdown and submit
        the search result handler.

        """
        self.open(self.SEARCH_BY_KEYWORD_URL)
        self.getControl('keywords').displayValue = [keyword]
        self.getControl('Search').click()
        if apply:
            self.getControl('Apply on selected persons').displayValue = [apply]
            self.getControl(name='form.buttons.apply').click()

    @property
    def submit_control_names(self):
        """List of the names of the submit controls in the form."""
        return self._get_control_names(
            zope.testbrowser.interfaces.ISubmitControl, self.getForm())

    @property
    def submit_control_names_all_forms(self):
        """List of the names of the submit controls in all forms."""
        forms = [self.getForm(index=index)
                 for index, _ in enumerate(self._getAllResponseForms())]
        names = [
            self._get_control_names(
                zope.testbrowser.interfaces.ISubmitControl, x)
            for x in forms]
        return names

    @property
    def all_control_names(self):
        """List of the names of all controls in the form."""
        return self._get_control_names(
            zope.testbrowser.interfaces.IControl, self.getForm())

    def in_out_widget_select(self, control_name, select_controls):
        """Add a selection to an in-out-widget.

        control_name ... name of the in-out-control, something like
                         'form.widgets.columns'
        select_controls ... list of control instances (item controls of in or
                             out list) which should be selected
        """
        form = self.getForm()
        for control in select_controls:
            webtest_form = form._form
            name = '%s:list' % control_name
            field = webtest.forms.Hidden(
                webtest_form, tag='input', name=name, pos=999,
                value=control.optionValue)
            webtest_form.fields.setdefault(name, []).append(field)
            webtest_form.field_order.append((name, field))

    def html_redirect(self):
        """Redirect as requested by ``<meta http-equiv="refresh" ... />``."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(self.contents, "lxml")
        meta = soup.find('meta')
        assert meta is not None, 'No <meta> tag found.'
        assert meta.get('http-equiv') == 'refresh', \
            '<meta http-equiv != "refresh"'
        url = meta.get('content').partition(';url=')[2]
        self.open(url)

    def _get_control_names(self, interface, form):
        """Get a sorted list of names of controls providing `interface`."""
        return sorted([control.name
                       for control in form.controls
                       if interface.providedBy(control)])


class Webdriver(object):
    """Wrapper around Selenese."""

    def __init__(self, selenium):
        self.selenium = selenium

    def login(self, username):
        transaction.commit()
        sel = self.selenium
        sel.open("http://{username}:{password}@{server}/".format(
                 username=username, server=self.selenium.server,
                 password=USERNAME_PASSWORD_MAP.get(username, username)))
        return sel

    @property
    def message(self):
        return self.selenium.getText('css=#info-messages')


# assertion helper functions and helper classes

def assert_forbidden(browser, username, url):
    """Assert accessing a URL is forbidden for a user."""
    browser.login(username)
    with pytest.raises(zope.testbrowser.browser.HTTPError) as err:
        browser.open(url)
    assert 'HTTP Error 403: Forbidden' == str(err.value)


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


class AddressBookAssertions:
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


class DateTimeClass(object):
    """Helper class to create and format datetime objects."""

    @property
    def now(self):
        return pytz.utc.localize(datetime.datetime.utcnow())

    def format(self, dt, force_date=False):
        """Format a datetime to the format needed in testbrowser."""
        if isinstance(dt, datetime.datetime) and not force_date:
            return dt.strftime('%y/%m/%d %H:%M')
        else:
            return self.format_date(dt)

    def format_date(self, dt):
        return "{0.year} {0.month} {0.day} ".format(dt)

    @staticmethod
    def add(dt, days=0, seconds=0):
        """Add some days and/or seconds to `dt`."""
        return dt + datetime.timedelta(days=days, seconds=seconds)


# Helper functions to create objects in the database

def create_addressbook(parent, name, title=None):
    """Create an address book in `parent`."""
    ab = icemac.addressbook.utils.create_obj(
        icemac.addressbook.addressbook.AddressBook)
    if title is not None:
        ab.title = title
    parent[name] = ab
    return ab


def create(address_book, parent, interface, set_as_default=False, *args, **kw):
    """Create an object using an entity.

    interface ... interface of the object which should be created.
    """
    with zope.component.hooks.site(address_book):
        entity = icemac.addressbook.interfaces.IEntity(interface)
        name = icemac.addressbook.utils.create_and_add(
            parent, entity.getClass(), *args)
        obj = parent[name]
        for key, value in kw.items():
            field = entity.getField(key)
            context = field.interface(obj)
            field.set(context, value)
        if set_as_default:
            field = icemac.addressbook.person.get_default_field(
                entity.interface)
            field.set(parent, obj)
        zope.lifecycleevent.modified(obj)
    return obj


def set_modified(obj, *args):
    """Set the modification date of an object."""
    dt = datetime.datetime(*args, tzinfo=pytz.utc)
    zope.dublincore.interfaces.IZopeDublinCore(obj).modified = dt
    return dt


def delete_field(browser, field_name):
    """Delete a user defined field."""
    manager = browser.login('mgr')
    manager.open(
        browser.ENTITY_PERSON_LIST_FIELDS_URL +
        '/{}/@@delete.html'.format(field_name))
    manager.getControl('Yes').click()
    assert manager.message.endswith('" deleted.')


# Helper functions and classes


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


def getRootFolder():
    """`TransactionMiddleware` expects a callable to get the root folder."""
    return CURRENT_CONNECTION.rootFolder


def interpolate_insted_of_translate(self, msgid, mapping=None, *args, **kw):
    """Use interpolation instead of translation."""
    return zope.i18n.interpolate(msgid, mapping)

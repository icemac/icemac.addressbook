# -*- coding: utf-8 -*-
import collections
import datetime
import gocept.jslint
import gocept.selenium.wsgi
import icemac.addressbook.address
import icemac.addressbook.addressbook
import icemac.addressbook.file.file
import icemac.addressbook.interfaces
import icemac.addressbook.keyword
import icemac.addressbook.person
import icemac.addressbook.principals.principals
import icemac.addressbook.principals.sources
import icemac.addressbook.startup
import icemac.addressbook.utils
import lxml.etree
import os
import os.path
import plone.testing
import plone.testing.zca
import plone.testing.zodb
import pytz
import transaction
import unittest
import z3c.etestbrowser.wsgi
import zope.annotation.attribute
import zope.app.publication.httpfactory
import zope.app.publication.zopepublication
import zope.app.wsgi
import zope.app.wsgi.testlayer
import zope.browserpage.metaconfigure
import zope.component
import zope.component.hooks
import zope.dublincore.interfaces
import zope.event
import zope.lifecycleevent
import zope.principalregistry.principalregistry
import zope.processlifetime
import zope.testbrowser.browser
import zope.testbrowser.interfaces
import zope.testbrowser.wsgi
import zope.testing.cleanup
import zope.testing.renormalizing


class _AddressBookUnitTests(plone.testing.Layer):
    """Layer for gathering addressbook unit tests."""

    defaultBases = (plone.testing.zca.LAYER_CLEANUP,)

    def setUp(self):
        # Some classes use gocept.reference and store default values for
        # which annotations are needed.
        zope.component.provideAdapter(
            zope.annotation.attribute.AttributeAnnotations)

    def tearDown(self):
        zope.testing.cleanup.tearDown()


class _ZCMLTearDownLayer(plone.testing.Layer):
    """Clear module globals set during ZCML set up."""

    def tearDown(self):
        # Needed so another ZCML layer can be run.
        zope.browserpage.metaconfigure.clear()
        zope.principalregistry.principalregistry.principalRegistry._clear()


class _ZODBLayer(plone.testing.zodb.EmptyZODB):
    """Layer which sets up ZODB to be useable for Zope 3."""

    def setUp(self):
        super(_ZODBLayer, self).setUp()
        zope.event.notify(zope.processlifetime.DatabaseOpened(self['zodbDB']))
        transaction.commit()

    def testSetUp(self):
        pass

    def testTearDown(self):
        pass


def setUpStackedDemoStorage(self, name):
    self['zodbDB'] = plone.testing.zodb.stackDemoStorage(
        self['zodbDB'], name=name)


ZODBConnection = collections.namedtuple(
    'ZODBConnection', ['connection', 'rootFolder', 'zodb'])


def createZODBConnection(zodbDB):
    """Create an open ZODB connection."""
    connection = zodbDB.open()
    rootFolder = connection.root()[
        zope.app.publication.zopepublication.ZopePublication.root_name]
    return ZODBConnection(connection, rootFolder, zodbDB)


def setUpZODBConnection(self):
    self['zodbConnection'], self['zodbRoot'], self['rootFolder'] = (
        createZODBConnection(self['zodbDB']))
    transaction.begin()


def tearDownZODBConnection(self):
    del self['rootFolder']
    transaction.abort()
    self['zodbConnection'].close()
    del self['zodbConnection']
    del self['zodbRoot']


def tearDownStackedDemoStorage(self):
    self['zodbDB'].close()
    del self['zodbDB']


class _ZODBIsolatedTestLayer(plone.testing.Layer):
    """Layer which puts a DemoStorage on ZODB for each test."""

    def testSetUp(self):
        setUpStackedDemoStorage(self, self.__name__)
        setUpZODBConnection(self)

    def testTearDown(self):
        tearDownStackedDemoStorage(self)
        tearDownZODBConnection(self)
        zope.component.hooks.setSite(None)


def setUpAddressBook(self):
    conn, rootObj, rootFolder = createZODBConnection(self['zodbDB'])
    addressbook = create_addressbook(rootFolder, 'ab')
    zope.component.hooks.setSite(addressbook)
    transaction.commit()
    # conn.close()
    return addressbook


class _AddressBookFunctionalLayer(plone.testing.Layer):
    "Layer where the address book gets created in the layer set up."

    def setUp(self):
        setUpStackedDemoStorage(self, 'AddressBookFunctionalTestCase')
        setUpAddressBook(self)

    def tearDown(self):
        tearDownStackedDemoStorage(self)

    def testSetUp(self):
        setUpZODBConnection(self)
        self['addressbook'] = self['rootFolder']['ab']
        zope.component.hooks.setSite(self['addressbook'])

    def testTearDown(self):
        tearDownZODBConnection(self)
        del self['addressbook']


class _WSGILayer(plone.testing.Layer):
    """Layer which sets up a WSGI stack."""

    def get_wsgi_pipeline(self):
        return icemac.addressbook.startup.application_factory(
            {}, db=self['zodbDB'])

    def setUp(self):
        self['wsgi_app'] = self.get_wsgi_pipeline()

    def tearDown(self):
        del self['wsgi_app']

    def testSetUp(self):
        # The layer has to store the database at layer set up (depending
        # layers require this) but we get a new database demo storage layer
        # at test set up, so we have to set the new ZODB here:
        app = self['wsgi_app']
        while not isinstance(app, zope.app.wsgi.WSGIPublisherApplication):
            # The outermost WSGI app not necessarily is our Zope app, so we
            # have to walk down the WSGI-Stack:
            if hasattr(app, 'app'):
                app = app.app
            else:
                app = app.wsgi_stack  # Used by AuthorizationMiddleware
        app.requestFactory = (
            zope.app.publication.httpfactory.HTTPPublicationRequestFactory(
                self['zodbDB']))


class _WSGITestBrowserLayer(plone.testing.Layer):
    """Layer for zope.testbrowser.wsgi tests."""

    def setUp(self):
        def getRootFolder():
            return self['rootFolder']
        self['wsgi_app'] = zope.testbrowser.wsgi.AuthorizationMiddleware(
            zope.app.wsgi.testlayer.TransactionMiddleware(
                getRootFolder, self['wsgi_app']))

    def tearDown(self):
        del self['wsgi_app']


class _AbstractDataLayer(plone.testing.Layer):
    """Base for layers creating data in the address book."""

    def setUp(self):
        setUpStackedDemoStorage(self, self.__class__.__name__)
        setupZODBConn, rootObj, rootFolder = createZODBConnection(
            self['zodbDB'])
        self.createData(rootFolder['ab'])
        transaction.commit()
        setupZODBConn.close()

    def createData(self, address_book):
        raise NotImplementedError('To be implemented by sub-class.')

    def removeData(self):
        """Remove data in tear down if necassary."""
        pass

    def tearDown(self):
        self.removeData()
        icemac.addressbook.testing.tearDownStackedDemoStorage(self)


# Layer factories

def ZCMLLayer(name, module, package, filename="ftesting.zcml"):
    """Factory to create a new ZCML test layer.

    name ... layer name, suffixed by 'ZCML'
    module ... usually `__name__`
    package ... package object, where the ftesting.zcml lives.
    """
    # A primary ZCML layer is a secondary one without a base + some teardown
    sandbox = SecondaryZCMLLayer(
        name, module, package, bases=None, filename=filename)
    return _ZCMLTearDownLayer(
        name="%sZCMLTearDown" % name, bases=[sandbox], module=module)


def SecondaryZCMLLayer(name, module, package, bases, filename="ftesting.zcml"):
    """Factory to create a new ZCML test layer above an existing one."""
    return plone.testing.zca.ZCMLSandbox(
        name="%sZCML" % name, bases=bases, filename=filename,
        module=module, package=package)


def ZODBLayer(name, zcml_layer):
    """Factory to create a ZODB test layer isolated on test level."""
    zodb_layer = _ZODBLayer(bases=[zcml_layer], name='%sZODBLayer' % name)
    isolated_layer = _ZODBIsolatedTestLayer(
        bases=[zodb_layer], name='%sZODBIsolatedLayer' % name)
    return _AddressBookFunctionalLayer(
        bases=[isolated_layer], name='%sSiteLayer' % name)


def TestBrowserLayer(name, zodb_layer):
    """Factory to create a layer for test browser based on WSGI."""
    wsgi_layer = _WSGILayer(bases=[zodb_layer], name='%sWSGILayer' % name)
    return _WSGITestBrowserLayer(
        bases=[wsgi_layer], name='%sTestBrowserLayer' % name)


# Predefined layers:
ADDRESS_BOOK_UNITTESTS = _AddressBookUnitTests(name='AddressBookUnitTests')
ZCML_LAYER = ZCMLLayer('AddressBook', __name__, icemac.addressbook)
ZODB_LAYER = ZODBLayer('AddressBook', ZCML_LAYER)
TEST_BROWSER_LAYER = TestBrowserLayer('AddressBook', ZODB_LAYER)


# Test layers including `locales` packages:
TRANSLATION_ZCML_LAYER = ZCMLLayer(
    'ABTranslation', __name__, icemac.addressbook, 'translationtesting.zcml')
TRANSLATION_ZODB_LAYER = ZODBLayer('ABTranslation', TRANSLATION_ZCML_LAYER)
TRANSLATION_TEST_BROWSER_LAYER = TestBrowserLayer(
    'ABTranslation', TRANSLATION_ZODB_LAYER)


def get_browser(layer, login=None):
    """Get a test browser.

    If `login` is not `None`: user is logged in via basic auth.

    """
    browser = Browser(wsgi_app=layer['wsgi_app'])
    if login is not None:
        browser.login(login)
    return browser


# Mixins
class ZODBMixIn(object):
    """Mix in methods for test cases basing on ZODB layer."""

    def create_person(self, last_name, **kw):
        ab = self.layer['addressbook']
        return create_person(ab, ab, last_name, **kw)


class BrowserMixIn(object):
    """Mix in methods for browser test cases."""

    def get_browser(self, login=None):
        """Get a test browser.

        If `login` is not `None`: user is logged in via basic auth.

        """
        return get_browser(self.layer, login)


# Test cases
class SeleniumTestCase(gocept.selenium.wsgi.TestCase):
    """Base test class for selenium tests."""
    layer = ZCML_LAYER
    level = 2

    def login(self, username='mgr', password='mgrpw'):
        transaction.commit()
        self.selenium.open("http://%s:%s@%s/" % (
            username, password, self.selenium.server))

    def assertMessage(self, text):
        self.selenium.assertText('css=#info-messages', text)


class BrowserTestCase(unittest.TestCase,
                      ZODBMixIn,
                      BrowserMixIn):
    """Test case for zope.testbrowser tests."""

    layer = TEST_BROWSER_LAYER
    maxDiff = None


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


# XXX see https://bitbucket.org/icemac/icemac.addressbook/issue/1
def _get_control_names(interface, browser=None, form=None):
    """Get a sorted list of names of controls providing the given interface.

    Whether the browser was given as argument the form of the browser is used.
    """
    if browser is not None:
        form = browser.getForm()
    else:
        browser = form.browser
    names = []
    for ctrl in form.mech_form.controls:
        control = zope.testbrowser.browser.controlFactory(ctrl, form, browser)
        if interface.providedBy(control):
            names.append(control.name)
    return sorted(names)


def get_submit_control_names(browser=None, form=None, all_forms=False):
    """Get a list of the names of the submit controls in the form.

    Whether the browser was given as argument the form of the browser is used.
    """
    if all_forms and browser:
        forms = [browser.getForm(index=x)
                 for x in range(len(list(browser.mech_browser.forms())))]
        browser = None
    else:
        forms = [form]

    names = [_get_control_names(
        zope.testbrowser.interfaces.ISubmitControl, browser, x)
        for x in forms]
    if not all_forms:
        # If we do not want to see all forms, do not nest the result into a
        # list:
        names = names[0]
    return names


def get_all_control_names(browser=None, form=None):
    """Get a list of all names of the controls in the form.

    Whether the browser was given as argument the form of the browser is used.
    """
    return _get_control_names(
        zope.testbrowser.interfaces.IControl, browser, form)


def in_out_widget_select(browser, control_name, select_controls):
    """Function to add a selection to an in-out-widget.

    browser ... testbrowser instance
    control_name ... name of the in-out-control, something like
                     form.widgets.columns
    select_controls ... list of control instances (item controls of in or out
                        list) which should be selected
    """
    form = browser.getForm()
    for control in select_controls:
        form.mech_form.new_control(
            type='hidden',
            name='%s:list' % control_name,
            attrs=dict(value=control.optionValue))


# List of users those passwords are not equal to the login name:
USERNAME_PASSWORD_MAP = dict(mgr='mgrpw')


class Browser(z3c.etestbrowser.wsgi.ExtendedTestBrowser):
    """Customized browser which provides login."""

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

    def login(self, username, password=None):
        """Login a user using basic auth."""
        if password is None:
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

    def logout(self):
        self.getLink('Logout').click()
        assert 'sfdgh' == self.message

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
        return get_submit_control_names(self)

    @property
    def all_control_names(self):
        """List of the names of all controls in the form."""
        return get_all_control_names(self)

    in_out_widget_select = in_out_widget_select

    # XXX deprecated, use submit_control_names property
    get_submit_control_names = get_submit_control_names
    # XXX deprecated, use all_control_names
    get_all_control_names = get_all_control_names


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


# Helper functions to create objects in the database

def create_addressbook(parent, name, title=None):
    """Create an address book.

    When parent is `None`, it gets created in the root folder of the data base.

    """
    ab = icemac.addressbook.utils.create_obj(
        icemac.addressbook.addressbook.AddressBook)
    if title is not None:
        ab.title = title
    parent[name] = ab
    return ab


@icemac.addressbook.utils.set_site
def create_keyword(title, return_obj=True):
    """Create a new keyword."""
    parent = zope.component.hooks.getSite().keywords
    name = icemac.addressbook.utils.create_and_add(
        parent, icemac.addressbook.keyword.Keyword, title=title)
    if return_obj:
        return parent[name]


@icemac.addressbook.utils.set_site
def create_person(parent, last_name, return_obj=True, **kw):
    """Create a new person in the address book.

    Caution: The created person is not editable trough the UI, as it
    is missing the default entries. See also `create_full_person`.
    """
    kw['last_name'] = last_name
    name = icemac.addressbook.utils.create_and_add(
        parent, icemac.addressbook.person.Person, **kw)
    if return_obj:
        return parent[name]


@icemac.addressbook.utils.set_site
def create_full_person(parent, last_name, return_obj=True, **kw):
    """Create a new person in the address book with all default entries.

    The created person is editable through the UI.
    """
    person = create_person(parent, parent, last_name, return_obj=True, **kw)
    create_postal_address(parent, person)
    create_email_address(parent, person)
    create_home_page_address(parent, person)
    create_phone_number(parent, person)
    if return_obj:
        return person


@icemac.addressbook.utils.set_site
def create_postal_address(person, set_as_default=True, return_obj=True, **kw):
    name = icemac.addressbook.utils.create_and_add(
        person, icemac.addressbook.address.PostalAddress, **kw)
    address = person[name]
    if set_as_default:
        person.default_postal_address = address
    if return_obj:
        return address


@icemac.addressbook.utils.set_site
def create_email_address(person, set_as_default=True, return_obj=True, **kw):
    name = icemac.addressbook.utils.create_and_add(
        person, icemac.addressbook.address.EMailAddress, **kw)
    address = person[name]
    if set_as_default:
        person.default_email_address = address
    if return_obj:
        return address


@icemac.addressbook.utils.set_site
def create_home_page_address(
        person, set_as_default=True, return_obj=True, **kw):
    name = icemac.addressbook.utils.create_and_add(
        person, icemac.addressbook.address.HomePageAddress, **kw)
    address = person[name]
    if set_as_default:
        person.default_home_page_address = address
    if return_obj:
        return address


@icemac.addressbook.utils.set_site
def create_phone_number(person, set_as_default=True, return_obj=True, **kw):
    name = icemac.addressbook.utils.create_and_add(
        person, icemac.addressbook.address.PhoneNumber, **kw)
    number = person[name]
    if set_as_default:
        person.default_phone_number = number
    if return_obj:
        return number


@icemac.addressbook.utils.set_site
def create_file(person, return_obj=True, **kw):
    "Create a file object inside the `person`."
    name = icemac.addressbook.utils.create_and_add(
        person, icemac.addressbook.file.file.File, **kw)
    if return_obj:
        return person[name]


@icemac.addressbook.utils.set_site
def create(parent, interface, set_as_default=False, *args, **kw):
    """Create an object using an entity.

    interface ... interface of the object which should be created.

    """
    entity = icemac.addressbook.interfaces.IEntity(interface)
    name = icemac.addressbook.utils.create_and_add(
        parent, entity.getClass(), *args)
    obj = parent[name]
    for key, value in kw.items():
        field = entity.getField(key)
        context = field.interface(obj)
        field.set(context, value)
    if set_as_default:
        field = icemac.addressbook.person.get_default_field(entity.interface)
        field.set(parent, obj)
    zope.lifecycleevent.modified(obj)
    return obj


@icemac.addressbook.utils.set_site
def create_field(entity_name_or_interface, type, title, **kw):
    """Create a user defined field for an entity.

    entity_name_or_interface ... Name used to register the entity as utility or
                                 or interface of the entity
    type ... see values of .sources.FieldTypeSource

    Returns the name of the created field.

    To create values for a Choice field use: values=<list of values>

    """
    field = icemac.addressbook.utils.create_obj(
        icemac.addressbook.entities.Field, type=type, title=title, **kw)
    if isinstance(entity_name_or_interface, basestring):
        entity = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntity,
            name=entity_name_or_interface)
    else:
        entity = icemac.addressbook.interfaces.IEntity(
            entity_name_or_interface)
    return entity.addField(field)


class InstallationAssertions(object):
    """Assertions helpful to check automatic installation routines."""

    def assertLocalUtility(self, ab, iface, name=''):
        self.assertIsNotNone(
            zope.component.queryUtility(iface, context=ab, name=name))

    def assertAttribute(self, ab, attribute, iface, name=''):
        self.assertTrue(iface.providedBy(getattr(ab, attribute)))
        self.assertLocalUtility(ab, iface, name)


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

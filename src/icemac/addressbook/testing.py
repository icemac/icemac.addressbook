# -*- coding: utf-8 -*-
# Copyright (c) 2009-2013 Michael Howitz
# See also LICENSE.txt
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
import inspect
import lxml.etree
import os
import os.path
import plone.testing
import plone.testing.zca
import plone.testing.zodb
import re
import tempfile
import transaction
import unittest2 as unittest
import z3c.etestbrowser.wsgi
import zope.annotation.attribute
import zope.app.publication.httpfactory
import zope.app.publication.zopepublication
import zope.app.wsgi
import zope.app.wsgi.testlayer
import zope.component
import zope.component.hooks
import zope.event
import zope.lifecycleevent
import zope.processlifetime
import zope.site.hooks
import zope.testbrowser.browser
import zope.testbrowser.interfaces
import zope.testbrowser.wsgi
import zope.testing.cleanup
import zope.testing.renormalizing
import zope.testrunner.layer

if os.environ.get('ZOPETESTINGDOCTEST'):  # pragma: no cover
    from zope.testing import doctest
else:
    import doctest


class _AddressBookUnitTests(plone.testing.Layer):
    """Layer for gathering addressbook unit tests."""
    defaultBases = (zope.testrunner.layer.UnitTests,)

    def setUp(self):
        # Some classes use gocept.reference and store default values for
        # which annotations are needed.
        zope.component.provideAdapter(
            zope.annotation.attribute.AttributeAnnotations)

    def tearDown(self):
        zope.testing.cleanup.tearDown()


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


def createZODBConnection(zodbDB):
    connection = zodbDB.open()
    zodbRoot = connection.root()
    rootFolder = zodbRoot[
        zope.app.publication.zopepublication.ZopePublication.root_name]
    return connection, zodbRoot, rootFolder


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
        zope.site.hooks.setSite(None)


def setUpAddressBook(self):
    conn, rootObj, rootFolder = createZODBConnection(self['zodbDB'])
    addressbook = create_addressbook(parent=rootFolder)
    zope.site.hooks.setSite(addressbook)
    transaction.commit()
    #conn.close()
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
        zope.site.hooks.setSite(self['addressbook'])

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
            app = app.app
        app.requestFactory = (
            zope.app.publication.httpfactory.HTTPPublicationRequestFactory(
                self['zodbDB']))


class _WSGITestBrowserLayer(zope.testbrowser.wsgi.Layer,
                            plone.testing.Layer):
    """Layer for zope.testbrowser.wsgi tests."""

    def make_wsgi_app(self):
        def getRootFolder():
            return self['rootFolder']
        # We could use zope.app.wsgi.testlayer.BrowserLayer but it extends
        # ZODBLayer which we do not want as a base class, so we have to
        # duplicate its middleware stack here:
        return zope.testbrowser.wsgi.AuthorizationMiddleware(
            zope.app.wsgi.testlayer.TransactionMiddleware(
                getRootFolder, self['wsgi_app']))


class _GoceptSeleniumPloneTestingIntegrationLayer(gocept.selenium.wsgi.Layer,
                                                  plone.testing.Layer):
    """Layer which integrates gocept.selenium with plone.testing."""

    def __init__(self, *args, **kw):
        # WSGI application is set up in base layers so we cannot access it
        # here yet:
        gocept.selenium.wsgi.Layer.__init__(self, application=None)
        plone.testing.Layer.__init__(self, *args, **kw)

    def setup_wsgi_stack(self, app):
        return self['wsgi_app']


# Layer factories

def ZCMLLayer(name, module, package, filename="ftesting.zcml", bases=None):
    """Factory to create a new ZCML test layer.

    name ... layer name, suffixed by 'ZCML'
    module ... usually `__name__`
    package ... where the ftesting.zcml lives.
    """
    return plone.testing.zca.ZCMLSandbox(
        name="%sZCML" % name, bases=bases, filename=filename, module=module,
        package=package)


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


def SeleniumLayer(name, zodb_layer):
    """Factory to create a new Selenium layer based on WSGI."""
    wsgi_layer = _WSGILayer(bases=[zodb_layer], name='%sWSGILayer' % name)
    return _GoceptSeleniumPloneTestingIntegrationLayer(
        bases=[wsgi_layer], name='%sSeleniumLayer' % name)


# Predefined layers
ADDRESS_BOOK_UNITTESTS = _AddressBookUnitTests(name='AddressBookUnitTests')
ZCML_LAYER = ZCMLLayer('AddressBook', __name__, icemac.addressbook)
ZODB_LAYER = ZODBLayer('AddressBook', ZCML_LAYER)
TEST_BROWSER_LAYER = TestBrowserLayer('AddressBook', ZODB_LAYER)
SELENIUM_LAYER = SeleniumLayer('AddressBook', ZODB_LAYER)


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
        browser = Browser()
        if login is not None:
            browser.login(login)
        return browser


# Test cases
class SeleniumTestCase(gocept.selenium.wsgi.TestCase):
    """Base test class for selenium tests."""
    layer = SELENIUM_LAYER
    level = 2

    def login(self, username='mgr', password='mgrpw'):
        transaction.commit()
        self.selenium.open("http://%s:%s@%s/" % (
            username, password, self.selenium.server))


class BrowserTestCase(unittest.TestCase,
                      ZODBMixIn,
                      BrowserMixIn):
    """Test case for zope.testbrowser tests."""

    layer = TEST_BROWSER_LAYER


def DocFileSuite(*paths, **kw):
    """Project specific DocFileSuite."""
    kw['optionflags'] = (kw.get('optionflags', 0) |
                         doctest.ELLIPSIS |
                         doctest.NORMALIZE_WHITESPACE)
    layer = kw.pop('layer')
    globs = kw.setdefault('globs', {})
    globs['layer'] = layer
    if 'checker' not in kw:
        kw['checker'] = zope.testing.renormalizing.RENormalizing([
            (re.compile(r'[0-9]{2}/[0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2}'),
             '<DATETIME>')
            ])
    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = layer
    return suite


def FunctionalDocFileSuite(*paths, **kw):
    """DocFileSuite on FUNCTIONAL_LAYER."""
    return DocFileSuite(layer=ZODB_LAYER, *paths, **kw)


def TestBrowserDocFileSuite(*paths, **kw):
    """DocFileSuite on TEST_BROWSER_LAYER."""
    return DocFileSuite(layer=TEST_BROWSER_LAYER, *paths, **kw)


# XXX see https://sourceforge.net/tracker/?func=detail&aid=3381282&group_id=273840&atid=2319598
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


def get_submit_control_names(browser=None, form=None):
    """Get a list of the names of the submit controls in the form.

    Whether the browser was given as argument the form of the browser is used.
    """
    return _get_control_names(
        zope.testbrowser.interfaces.ISubmitControl, browser, form)


def get_all_control_names(browser=None, form=None):
    """Get a list of all names of the controls in the form.

    Whether the browser was given as argument the form of the browser is used.
    """
    return _get_control_names(
        zope.testbrowser.interfaces.IControl, browser, form)


def get_messages(browser):
    """Return the info messages displayed in browser.

    Returns string when there is exactly one message, list otherwise."""
    if not isinstance(browser, z3c.etestbrowser.wsgi.ExtendedTestBrowser):
        raise ValueError(
            'browser must be z3c.etestbrowser.wsgi.ExtendedTestBrowser')
    return [x.text
            for x in browser.etree.xpath('//div[@id="info-messages"]/ul/li')]


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


def write_temp_file(content, suffix):
    "Write `content` to a temporary file and return file handle and file name."
    fd, filename = tempfile.mkstemp(suffix=suffix)
    os.write(fd, content)
    os.close(fd)
    return file(filename, 'r'), os.path.basename(filename)


# List of users those passwords are not equal to the login name:
USERNAME_PASSWORD_MAP = dict(mgr='mgrpw')


class Browser(z3c.etestbrowser.wsgi.ExtendedTestBrowser):
    """Customized browser which provides login."""

    def login(self, username):
        """Login a user using basic auth."""
        self.addHeader(
            'Authorization', 'Basic %s:%s' %
            (username, USERNAME_PASSWORD_MAP.get(username, username)))

    def etree_to_list(self, etree):
        """"Convert an etree into a list (lines without leading whitespace.)"""
        return [x.strip()
                for x in lxml.etree.tostring(etree).split('\n')
                if x.strip()]

    get_messages = get_messages
    get_all_control_names = get_all_control_names
    in_out_widget_select = in_out_widget_select

### Helper functions to create objects in the database ###


def create_addressbook(name='ab', title=None, parent=None):
    """Create an address book.

    When parent is `None`, it gets created in the root folder of the data base.

    """
    ab = icemac.addressbook.utils.create_obj(
        icemac.addressbook.addressbook.AddressBook)
    if title is not None:
        ab.title = title
    if parent is None:
        frame = inspect.currentframe()
        try:
            parent = frame.f_back.f_globals['layer']['rootFolder']
        finally:
            del frame
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
def create(
    parent, entity_name, return_obj=False, set_as_default=False, *args, **kw):
    """Create an object using an entity.

    entity_name ... IEntity.class_name

    """
    entity = zope.component.getUtility(
        icemac.addressbook.interfaces.IEntity, name=entity_name)
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
    if return_obj:
        return obj


@icemac.addressbook.utils.set_site
def create_user(ab, first_name, last_name, email, password, roles, **kw):
    person = create_person(
        ab, ab, last_name, first_name=first_name, **kw)
    create_email_address(ab, person, email=email)

    role_factory = icemac.addressbook.principals.sources.role_source.factory
    role_values = role_factory.getValues()
    selected_roles = []
    for role_title in roles:
        for candidate in role_values:
            if role_factory.getTitle(candidate) == role_title:
                selected_roles.append(candidate)
                break
    icemac.addressbook.utils.create_and_add(
        ab.principals, icemac.addressbook.principals.principals.Principal,
        person=person, password=password, roles=selected_roles)


@icemac.addressbook.utils.set_site
def create_field(entity_name_or_interface, type, title, **kw):
    """Create a user defined field for an entity.

    entity_name ... Name used to register the entity as utility
    type ... see values of .sources.FieldTypeSource

    Returns the name of the created field.

    To create values for a Choice field use: values=<list of values>

    """
    field = icemac.addressbook.utils.create_obj(
        icemac.addressbook.entities.Field, type=type, title=title, **kw)
    if isinstance(entity_name_or_interface, basestring):
        entity = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntity, name=entity_name)
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

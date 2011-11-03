# -*- coding: utf-8 -*-
# Copyright (c) 2009-2011 Michael Howitz
# See also LICENSE.txt
# $Id$

import gocept.selenium.grok
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
import os
import os.path
import plone.testing
import plone.testing.zca
import plone.testing.zodb
import re
import tempfile
import transaction
import z3c.etestbrowser.wsgi
import zope.annotation.attribute
import zope.app.publication.httpfactory
import zope.app.publication.zopepublication
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

ADDRESS_BOOK_UNITTESTS = _AddressBookUnitTests(name='AddressBookUnitTests')


class _ZCMLAndZODBLayer(plone.testing.zodb.EmptyZODB):
    """Layer which sets up ZCML and ZODB to be useable for Zope 3."""
    defaultBases = (plone.testing.zca.LAYER_CLEANUP,)

    package = icemac.addressbook

    def setUp(self):
        super(_ZCMLAndZODBLayer, self).setUp()
        plone.testing.zca.setUpZcmlFiles(
            [("ftesting.zcml", self.package)])
        zope.event.notify(zope.processlifetime.DatabaseOpened(self['zodbDB']))
        transaction.commit()

    def tearDown(self):
        plone.testing.zca.tearDownZcmlFiles()
        super(_ZCMLAndZODBLayer, self).tearDown()

    def testSetUp(self):
        pass

    def testTearDown(self):
        pass


ZCML_AND_ZODB_LAYER = _ZCMLAndZODBLayer(name='ZCMLAndZODBLayer')


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


class _ZODBTestLayer(plone.testing.Layer):
    """Layer which opens the ZODB for each test."""
    defaultBases = (ZCML_AND_ZODB_LAYER,)

    def testSetUp(self):
        setUpZODBConnection(self)

    def testTearDown(self):
        tearDownZODBConnection(self)

FUNCTIONAL_LAYER = _ZODBTestLayer(name='ZODBTestLayer')


class _ZODBIsolatedTestLayer(plone.testing.Layer):
    """Layer which puts a DemoStorage on ZODB for each test."""
    defaultBases = (ZCML_AND_ZODB_LAYER,)

    def testSetUp(self):
        setUpStackedDemoStorage(self, self.__name__)
        setUpZODBConnection(self)

    def testTearDown(self):
        tearDownStackedDemoStorage(self)
        tearDownZODBConnection(self)

ZODB_ISOLATED_TEST_LAYER = _ZODBIsolatedTestLayer(name='ZODBIsolatedTestLayer')


class WSGILayer(plone.testing.Layer):
    """Layer which sets up a WSGI stack."""
    defaultBases = (ZODB_ISOLATED_TEST_LAYER,)

    def get_wsgi_pipeline(self):
        return icemac.addressbook.startup.application_factory(
            {}, db=self['zodbDB'])

    def setUp(self):
        self['wsgi_app'] = self.get_wsgi_pipeline()

    def tearDown(self):
        del self['wsgi_app']

WSGI_LAYER = WSGILayer()


class _WSGITestBrowserLayer(zope.testbrowser.wsgi.Layer,
                            plone.testing.Layer):
    """Layer for zope.testbrowser.wsgi tests."""
    defaultBases = (WSGI_LAYER,)

    def make_wsgi_app(self):
        def getRootFolder():
            return self['rootFolder']
        # We could use zope.app.wsgi.testlayer.BrowserLayer but it extends
        # ZODBLayer which we do not want as a base class, so we have to
        # duplicate its middleware stack here:
        return zope.testbrowser.wsgi.AuthorizationMiddleware(
            zope.app.wsgi.testlayer.TransactionMiddleware(
                getRootFolder, self['wsgi_app']))

    def testSetUp(self):
        # WSGI app stores the database at layer set up but we get a new
        # database at test set up, so we have to set the right ZODB here:
        self['wsgi_app'].requestFactory = (
            zope.app.publication.httpfactory.HTTPPublicationRequestFactory(
                self['zodbDB']))


WSGI_TEST_BROWSER_LAYER = _WSGITestBrowserLayer(name='WSGITestBrowserLayer')


SeleniumLayer = gocept.selenium.grok.Layer(
    icemac.addressbook, name='SeleniumLayer')


def setUpAddressBook(self):
    self.old_site = zope.site.hooks.getSite()
    conn, rootObj, rootFolder = createZODBConnection(self['zodbDB'])
    addressbook = create_addressbook(parent=rootFolder)
    zope.site.hooks.setSite(addressbook)
    transaction.commit()
    conn.close()
    return addressbook


class _AddressBookFunctionalLayer(plone.testing.Layer):
    "Layer where the address book gets created in the layer set up."
    defaultBases = (ZCML_AND_ZODB_LAYER,)

    def setUp(self):
        setUpStackedDemoStorage(self, 'AddressBookFunctionalTestCase')
        self['addressbook'] = setUpAddressBook(self)

    def tearDown(self):
        zope.site.hooks.setSite(self.old_site)
        del self['addressbook']
        tearDownStackedDemoStorage(self)

    def testSetUp(self):
        setUpZODBConnection(self)
        zope.site.hooks.setSite(self['addressbook'])

    def testTearDown(self):
        tearDownZODBConnection(self)

ADDRESS_BOOK_FUNCTIONAL_LAYER = _AddressBookFunctionalLayer(
    name='AddressBookFunctionalLayer')


# Layer to use ADDRESS_BOOK_FUNCTIONAL_LAYER with testbrowser:
WSGI_ADDRESS_BOOK_FUNCTIONAL_LAYER = _WSGITestBrowserLayer(
    bases=[WSGILayer(bases=[ZODB_ISOLATED_TEST_LAYER,
                            ADDRESS_BOOK_FUNCTIONAL_LAYER],
                     name='WSGIAddressBookFunctionalLayer')],
    name='TestBrowserAddressBookFunctionalLayer')


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
    return DocFileSuite(layer=FUNCTIONAL_LAYER, *paths, **kw)


def TestBrowserDocFileSuite(*paths, **kw):
    """DocFileSuite on WSGI_TEST_BROWSER_LAYER."""
    return DocFileSuite(layer=WSGI_TEST_BROWSER_LAYER, *paths, **kw)


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


# List of known users which are able to login using basic auth:
USERNAME_PASSWORD_MAP = dict(mgr='mgrpw', editor='editor', visitor='visitor')


class Browser(z3c.etestbrowser.wsgi.ExtendedTestBrowser):
    """Customized browser which provides login."""

    def login(self, username):
        """Login a user using basic auth."""
        self.addHeader('Authorization', 'Basic %s:%s' %
                       (username, USERNAME_PASSWORD_MAP[username]))

    get_messages = get_messages


### Helper functions to create objects in the database ###


def create_addressbook(name='ab', title=u'test address book', parent=None):
    """Create an address book.

    When parent is `None`, it gets created in the root folder of the data base.

    """
    ab = icemac.addressbook.utils.create_obj(
        icemac.addressbook.addressbook.AddressBook, title=title)
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
def create_field(entity_name, type, title, **kw):
    """Create a user defined field for an entity.

    entity_name ... IEntity.class_name
    type ... see values of .sources.FieldTypeSource

    Returns the name of the created field.

    To create values for a Choice field use: values=<list of values>

    """
    field = icemac.addressbook.utils.create_obj(
        icemac.addressbook.entities.Field, type=type, title=title, **kw)
    entity = zope.component.getUtility(
        icemac.addressbook.interfaces.IEntity, name=entity_name)
    return entity.addField(field)

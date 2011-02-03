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
import icemac.addressbook.utils
import inspect
import os
import os.path
import re
import tempfile
import unittest
import z3c.etestbrowser.wsgi
import zope.annotation.attribute
import zope.app.wsgi.testlayer
import zope.component
import zope.site.hooks
import zope.testbrowser.browser
import zope.testbrowser.interfaces
import zope.testing.cleanup
import zope.testing.renormalizing
import zope.testrunner.layer

if os.environ.get('ZOPETESTINGDOCTEST'): # pragma: no cover
    from zope.testing import doctest
else:
    import doctest


class AddressBookUnitTests(zope.testrunner.layer.UnitTests):
    """Layer for gathering addressbook unit tests."""

    @classmethod
    def setUp(cls):
        # Some classes use gocept.reference and store default values for
        # which annotations are needed.
        zope.component.provideAdapter(
            zope.annotation.attribute.AttributeAnnotations)

    @classmethod
    def tearDown(cls):
        zope.testing.cleanup.tearDown()


def UnittestSuite(*classes):
    """Create a unittest test suite from unittest test classes."""
    suite = unittest.TestSuite()
    for class_ in classes:
        suite.addTest(unittest.makeSuite(class_))
    return suite


def AddressBookUnittestSuite(*classes):
    """Create a unittest test suite on addressbook layer."""
    suite = UnittestSuite(*classes)
    suite.layer = AddressBookUnitTests
    return suite


FunctionalLayer = zope.app.wsgi.testlayer.BrowserLayer(icemac.addressbook)
SeleniumLayer = gocept.selenium.grok.Layer(
    icemac.addressbook, name='SeleniumLayer')


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FunctionalLayer


class AddressBookFunctionalTestCase(FunctionalTestCase):
    "Functional test case where the address book gets created in the set up."

    def setUp(self):
        super(AddressBookFunctionalTestCase, self).setUp()
        self.old_site = zope.site.hooks.getSite()
        zope.site.hooks.setSite(
            icemac.addressbook.testing.create_addressbook(
                parent=self.layer.getRootFolder()))

    def tearDown(self):
        super(AddressBookFunctionalTestCase, self).tearDown()
        zope.site.hooks.setSite(self.old_site)


def FunctionalDocFileSuite(*paths, **kw):
    kw['optionflags'] = (kw.get('optionflags', 0) |
                         doctest.ELLIPSIS |
                         doctest.NORMALIZE_WHITESPACE)
    if 'layer' in kw:
        layer = kw.pop('layer')
    else:
        layer = FunctionalLayer
    globs = kw.setdefault('globs', {})
    globs['getRootFolder'] = layer.getRootFolder
    if 'checker' not in kw:
        kw['checker'] = zope.testing.renormalizing.RENormalizing([
            (re.compile(r'[0-9]{2}/[0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2}'),
             '<DATETIME>')
            ])
    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = layer
    return suite


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


### Helper functions to create objects in the database ###


def create_addressbook(name='ab', title=u'test address book', parent=None):
    """Create an address book.

    When parent is `None`, it gets created in the root folder of the data base.

    """
    ab = icemac.addressbook.utils.create_obj(
        icemac.addressbook.addressbook.AddressBook, title=title)
    frame = inspect.currentframe()
    if parent is None:
        try:
            parent = frame.f_back.f_globals['getRootFolder']()
        finally:
            del frame
    parent[name] = ab
    return ab


def create_keyword(addressbook, title, return_obj=True):
    parent = addressbook.keywords
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

    entity_name ... module name and class name of entity

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

    entity_name ... module name and class name of entity
    type ... see values of sources.FieldTypeSource

    """
    field = icemac.addressbook.utils.create_obj(
        icemac.addressbook.entities.Field, type=type, title=title, **kw)
    entity = zope.component.getUtility(
        icemac.addressbook.interfaces.IEntity, name=entity_name)
    entity.addField(field)

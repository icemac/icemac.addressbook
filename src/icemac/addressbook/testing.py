# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt
# $Id$

import doctest
import icemac.addressbook.address
import icemac.addressbook.addressbook
import icemac.addressbook.keyword
import icemac.addressbook.person
import icemac.addressbook.principals.principals
import icemac.addressbook.principals.sources
import icemac.addressbook.utils
import os
import os.path
import tempfile
import unittest
import zope.annotation.attribute
import zope.app.testing.functional
import zope.testbrowser.browser
import zope.testbrowser.interfaces
import zope.testing.cleanup
import zope.testing.testrunner.layer

class AddressBookUnitTests(zope.testing.testrunner.layer.UnitTests):
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


# XXX zope.app.testing.functional.defineLayer benutzen
ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = zope.app.testing.functional.ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer')


class FunctionalTestCase(zope.app.testing.functional.FunctionalTestCase):
    """Base class for functional tests."""

    layer = FunctionalLayer


def FunctionalDocFileSuite(*paths, **kw):
    kw['optionflags'] = (kw.get('optionflags', 0) |
                         doctest.ELLIPSIS |
                         doctest.NORMALIZE_WHITESPACE)
    if kw.has_key('layer'):
        layer = kw.pop('layer')
    else:
        layer = FunctionalLayer
    suite = zope.app.testing.functional.FunctionalDocFileSuite(*paths, **kw)
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


def write_temp_file(content, suffix):
    "Write `content` to a temporary file and return file handle and file name."
    fd, filename = tempfile.mkstemp(suffix=suffix)
    os.write(fd, content)
    os.close(fd)
    return file(filename, 'r'), os.path.basename(filename)


def create_addressbook(parent=None, name='ab', title=u'test address book'):
    ab = icemac.addressbook.utils.create_obj(
        icemac.addressbook.addressbook.AddressBook, title=title)
    if parent is None:
        parent = zope.app.testing.functional.getRootFolder()
    parent[name] = ab
    return ab


def create_keyword(addressbook, title, notes=u''):
    parent = addressbook.keywords
    name = icemac.addressbook.utils.create_and_add(
        parent, icemac.addressbook.keyword.Keyword, title=title, notes=notes)
    return parent[name]


@icemac.addressbook.utils.set_site
def create_person(parent, last_name, return_obj=True, **kw):
    kw['last_name'] = last_name
    name = icemac.addressbook.utils.create_and_add(
        parent, icemac.addressbook.person.Person, **kw)
    if return_obj:
        return parent[name]


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
def create_user(ab, first_name, last_name, email, password, roles):
    person = create_person(
        ab, ab, last_name, first_name=first_name)
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

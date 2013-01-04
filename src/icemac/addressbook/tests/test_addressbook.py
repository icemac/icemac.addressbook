# -*- coding: latin-1 -*-
# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.addressbook
import icemac.addressbook.interfaces
import icemac.addressbook.testing
import icemac.addressbook.utils
import unittest2 as unittest
import zope.authentication.interfaces
import zope.catalog.interfaces
import zope.intid.interfaces
import zope.location.interfaces
import zope.pluggableauth.interfaces


class TestAddressbook(unittest.TestCase,
                      icemac.addressbook.testing.InstallationAssertions):

    layer = icemac.addressbook.testing.ZODB_LAYER

    def check_addressbook(self, ab):
        self.assertTrue(zope.location.interfaces.ISite.providedBy(ab))
        self.assertAttribute(
            ab, 'keywords', icemac.addressbook.interfaces.IKeywords)
        self.assertAttribute(
            ab, 'principals',
            zope.pluggableauth.interfaces.IAuthenticatorPlugin,
            name=u'icemac.addressbook.principals')
        self.assertAttribute(
            ab, 'entities',
            icemac.addressbook.interfaces.IEntities)
        self.assertAttribute(
            ab, 'orders',
            icemac.addressbook.interfaces.IOrderStorage)
        self.assertLocalUtility(ab, zope.intid.interfaces.IIntIds)
        self.assertLocalUtility(ab, zope.catalog.interfaces.ICatalog)
        self.assertLocalUtility(
            ab, zope.authentication.interfaces.IAuthentication)

    def setUp(self):
        super(TestAddressbook, self).setUp()
        self.ab = self.layer['addressbook']

    def test_create(self):
        self.check_addressbook(self.ab)

    def test_recall_create_infrastructure(self):
        icemac.addressbook.addressbook.create_address_book_infrastructure(
            self.ab)
        self.check_addressbook(self.ab)

    def test___repr___no___name__(self):
        self.assertEqual("<AddressBook None (None)>",
                         repr(icemac.addressbook.addressbook.AddressBook()))

    def test___repr___no_title(self):
        self.assertEqual("<AddressBook u'ab' (None)>", repr(self.ab))

    def test___repr__(self):
        self.ab.title = u'My address book'
        self.assertEqual("<AddressBook u'ab' (u'My address book')>",
                         repr(self.ab))

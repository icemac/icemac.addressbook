# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.addressbook
import icemac.addressbook.interfaces
import icemac.addressbook.testing
import zope.location.interfaces
import zope.intid.interfaces
import zope.catalog.interfaces
import zope.authentication.interfaces
import zope.app.authentication.interfaces
import icemac.addressbook.utils


class TestAddressbook(icemac.addressbook.testing.FunctionalTestCase):

    def assertLocalUtility(self, ab, iface):
        self.assertTrue(
            icemac.addressbook.addressbook.utility_locally_registered(ab, iface)
            )

    def assertAttribute(self, ab, attribute, iface):
        self.assertTrue(iface.providedBy(getattr(ab, attribute)))
        self.assertLocalUtility(ab, iface)

    def check_addressbook(self, ab):
        self.assertTrue(zope.location.interfaces.ISite.providedBy(ab))
        self.assertAttribute(
            ab, 'keywords', icemac.addressbook.interfaces.IKeywords)
        self.assertAttribute(
            ab, 'principals',
            zope.app.authentication.interfaces.IAuthenticatorPlugin)
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
        root = self.getRootFolder()
        root['ab'] = self.ab = icemac.addressbook.utils.create_obj(
            icemac.addressbook.addressbook.AddressBook)

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

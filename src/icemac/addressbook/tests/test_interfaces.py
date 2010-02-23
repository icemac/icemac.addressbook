# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt

import gocept.reference.verify
import icemac.addressbook.address
import icemac.addressbook.addressbook
import icemac.addressbook.entities
import icemac.addressbook.interfaces
import icemac.addressbook.keyword
import icemac.addressbook.orderstorage
import icemac.addressbook.person
import icemac.addressbook.testing
import unittest
import zope.component.testing
import zope.interface
import zope.interface.verify


class TestInterfaces(unittest.TestCase):

    def tearDown(self):
        zope.component.testing.tearDown()

    def test_person(self):
        person = icemac.addressbook.person.Person()
        gocept.reference.verify.verifyObject(
            icemac.addressbook.interfaces.IPerson, person)

        gocept.reference.verify.verifyObject(
            icemac.addressbook.interfaces.IPersonDefaults, person)

    def test_address_book(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IAddressBook,
            icemac.addressbook.addressbook.AddressBook())

    def test_postal_address(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IPostalAddress,
            icemac.addressbook.address.PostalAddress())

    def test_email_address(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IEMailAddress,
            icemac.addressbook.address.EMailAddress())

    def test_home_page_address(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IHomePageAddress,
            icemac.addressbook.address.HomePageAddress())

    def test_phone_number(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IPhoneNumber,
            icemac.addressbook.address.PhoneNumber())

    def test_keywords(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IKeywords,
            icemac.addressbook.keyword.KeywordContainer())

    def test_keyword(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IKeyword,
            icemac.addressbook.keyword.Keyword())

    def test_keywordtitles(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IKeywordTitles,
            icemac.addressbook.person.Keywords(None))

    def test_entities(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IEntities,
            icemac.addressbook.entities.Entities())
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IEntities,
            icemac.addressbook.entities.PersistentEntities())

    def test_entity(self):
        class IE(zope.interface.Interface):
            pass
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IEntity,
            icemac.addressbook.entities.Entity(
                u'E', IE, 'icemac.addressbook.TestInterfaces'))

    def test_field(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IField,
            icemac.addressbook.entities.Field())

    def test_orderstorage_read(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IOrderStorageRead,
            icemac.addressbook.orderstorage.OrderStorage())

    def test_orderstorage_write(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IOrderStorageWrite,
            icemac.addressbook.orderstorage.OrderStorage())

    def test_orderstorage_rw(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IOrderStorage,
            icemac.addressbook.orderstorage.OrderStorage())



def test_suite():
    return icemac.addressbook.testing.UnittestSuite(TestInterfaces)


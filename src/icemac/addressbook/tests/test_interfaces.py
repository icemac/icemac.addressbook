# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt

import gocept.reference.verify
import icemac.addressbook.address
import icemac.addressbook.addressbook
import icemac.addressbook.fields
import icemac.addressbook.interfaces
import icemac.addressbook.keyword
import icemac.addressbook.entities
import icemac.addressbook.person
import icemac.addressbook.testing
import unittest
import zope.interface.verify


class TestInterfaces(unittest.TestCase):

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

    def test_fields(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IFields,
            icemac.addressbook.fields.Fields())
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IFields,
            icemac.addressbook.fields.PersistentFields())

    def test_field(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IField,
            icemac.addressbook.fields.Field())

def test_suite():
    return icemac.addressbook.testing.UnittestSuite(TestInterfaces)


# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.fields
import icemac.addressbook.interfaces
import unittest
import zope.schema
import icemac.addressbook.entities


class TestEntities(unittest.TestCase):

    def setUp(self):
        self.entities = icemac.addressbook.entities.Entities()

    def test_getPrefixes(self):
        self.assertEqual(
            ['address_book',
             'person',
             'postal_address',
             'phone_number',
             'email_address',
             'home_page_address',
             'file',
             'keyword',
             'principal'], self.entities.getPrefixes())

    def test_getTitle_unknown_type(self):
        self.assertRaises(TypeError, self.entities.getTitle, None)

    def test_getTitle_unknown_prefix(self):
        self.assertRaises(ValueError, self.entities.getTitle, 'asdf')

    def test_getTitle_known_prefix(self):
        self.assertEqual(_(u'Person'), self.entities.getTitle('person'))

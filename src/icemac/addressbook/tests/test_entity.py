# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.entities
import icemac.addressbook.interfaces
import unittest
import zope.component.testing
import zope.interface
import zope.interface.exceptions
import zope.schema


class IDummy(zope.interface.Interface):

    dummy = zope.schema.Text(title=u'dummy')
    dummy2 = zope.schema.Text(title=u'dummy2')


class Dummy(object):
    pass


class TestEntity(unittest.TestCase):

    def setUp(self):
        self.entity = icemac.addressbook.entities.Entity(
            u'Dummy', IDummy, 'icemac.addressbook.tests.test_entity.Dummy')

    def tearDown(self):
        zope.component.testing.tearDown()

    def test_getFieldsInOrder_static_fields(self):
        self.assertEqual(
            [('dummy', IDummy['dummy']),
             ('dummy2', IDummy['dummy2'])],
            self.entity.getFieldsInOrder())

    def test_getFieldValuesInOrder(self):
        self.assertEqual(
            [IDummy['dummy'], IDummy['dummy2']],
            self.entity.getFieldValuesInOrder())

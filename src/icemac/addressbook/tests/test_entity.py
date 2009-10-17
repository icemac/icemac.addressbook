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


class Factory(object):

    def __init__(self, obj):
        self._obj = obj

    def __call__(self, *args):
        return self._obj


class TestEntity(unittest.TestCase):

    def setUp(self):
        self.entity = icemac.addressbook.entities.Entity(
            u'Dummy', IDummy, 'icemac.addressbook.tests.test_entity.Dummy')

        self.user_field = icemac.addressbook.entities.Field()
        self.user_field.__name__ = 'Field#1'
        self.user_field.type = 'TextLine'
        zope.component.provideAdapter(
            Factory(self.user_field),
            adapts=(icemac.addressbook.interfaces.IEntity, IDummy),
            provides=icemac.addressbook.interfaces.IField,
            name=self.user_field.__name__)
        self.schemaized_field = (
            icemac.addressbook.entities.user_field_to_schema_field(
                self.user_field))

    def tearDown(self):
        zope.component.testing.tearDown()

    def test_getRawFields(self):
        self.assertEqual([('dummy', IDummy['dummy']),
                          ('dummy2', IDummy['dummy2']),
                          ('Field#1', self.user_field),],
                         list(self.entity.getRawFields()))

    def test_getFieldsInOrder(self):
        self.assertEqual([('dummy', IDummy['dummy']),
                          ('dummy2', IDummy['dummy2']),
                          ('Field#1', self.schemaized_field),],
                         list(self.entity.getFieldsInOrder()))

    def test_getFieldValuesInOrder(self):
        self.assertEqual(
            [IDummy['dummy'], IDummy['dummy2'], self.schemaized_field],
            self.entity.getFieldValuesInOrder())

    def test_getClass(self):
        self.assertEqual(Dummy, self.entity.getClass())

    def test_getClass_no_class_set(self):
        e = icemac.addressbook.entities.Entity(None, IDummy, None)
        self.assertRaises(ValueError, e.getClass)

# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.entities
import icemac.addressbook.interfaces
import unittest
import zope.component.testing
import zope.container.contained
import zope.container.sample
import zope.interface
import zope.schema


class IDummy(zope.interface.Interface):

    dummy = zope.schema.Text(title=u'dummy')
    dummy2 = zope.schema.Text(title=u'dummy2')


class Dummy(object):
    zope.interface.implements(IDummy)


class TestEntity(unittest.TestCase):

    def setUp(self):
        # Entities
        entities = zope.container.sample.SampleContainer()
        zope.interface.directlyProvides(
            entities, icemac.addressbook.interfaces.IEntities)
        zope.component.provideUtility(
            entities, icemac.addressbook.interfaces.IEntities)
        zope.component.provideAdapter(
            zope.container.contained.NameChooser,
            [icemac.addressbook.interfaces.IEntities])

        # Entity under test
        self.entity = icemac.addressbook.entities.Entity(
            u'Dummy', IDummy, 'icemac.addressbook.tests.test_entity.Dummy')

        # Field under test
        self.user_field = icemac.addressbook.entities.Field()
        self.user_field.type = 'TextLine'
        self.entity.addField(self.user_field)
        self.schemaized_field = (
            icemac.addressbook.entities.user_field_to_schema_field(
                self.user_field))

    def tearDown(self):
        zope.component.testing.tearDown()

    # IEntityWrite

    def test_add_field_storage(self):
        entities = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntities)
        self.assertTrue(self.user_field is entities[u'Field'])

    def test_add_field_adapter_registration(self):
        field = zope.component.getMultiAdapter(
            (self.entity, Dummy()),
            icemac.addressbook.interfaces.IField, name=u'Field')
        self.assertTrue(self.user_field is field)

    # IEntityRead

    def test_name(self):
        self.assertEqual('IcemacAddressbookTestsTestEntityDummy',
                         self.entity.name)

    def test_name_no_class_name_set(self):
        self.assertRaises(
            ValueError, getattr,
            icemac.addressbook.entities.Entity(None, IDummy, None), "name")

    def test_getRawFields(self):
        self.assertEqual([('dummy', IDummy['dummy']),
                          ('dummy2', IDummy['dummy2']),
                          ('Field', self.user_field)],
                         list(self.entity.getRawFields()))

    def test_getFieldsInOrder(self):
        self.assertEqual([('dummy', IDummy['dummy']),
                          ('dummy2', IDummy['dummy2']),
                          ('Field', self.schemaized_field)],
                         list(self.entity.getFieldsInOrder()))

    def test_getFieldValuesInOrder(self):
        self.assertEqual(
            [IDummy['dummy'], IDummy['dummy2'], self.schemaized_field],
            self.entity.getFieldValuesInOrder())

    def test_getField_unknown_field(self):
        self.assertRaises(KeyError, self.entity.getField, 'asdf')

    def test_getField_schema_field(self):
        self.assertEqual(IDummy['dummy2'], self.entity.getField('dummy2'))

    def test_getField_user_field(self):
        self.assertEqual(
            self.schemaized_field, self.entity.getField('Field'))

    def test_getRawField_unknown_field(self):
        self.assertRaises(KeyError, self.entity.getRawField, 'asdf')

    def test_getRawField_schema_field(self):
        self.assertEqual(IDummy['dummy2'], self.entity.getRawField('dummy2'))

    def test_getRawField_user_field(self):
        self.assertEqual(
            self.user_field, self.entity.getRawField('Field'))

    def test_getClass(self):
        self.assertEqual(Dummy, self.entity.getClass())

    def test_getClass_no_class_set(self):
        e = icemac.addressbook.entities.Entity(None, IDummy, None)
        self.assertRaises(ValueError, e.getClass)

    def test_tagged_values(self):
        e = icemac.addressbook.entities.Entity(
            u'Dummy', IDummy, 'Dummy', a=1, b='asdf')
        self.assertEqual(dict(a=1, b='asdf'), e.tagged_values)

    def test_tagged_values_returns_copy(self):
        # Tagged values not modifyable by modifying the returned dict.
        e = icemac.addressbook.entities.Entity(
            u'Dummy', IDummy, 'Dummy', a=1, b='asdf')
        e.tagged_values['a'] = 2
        self.assertEqual(dict(a=1, b='asdf'), e.tagged_values)

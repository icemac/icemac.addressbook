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

        # Order storage
        storage = icemac.addressbook.orderstorage.OrderStorage()
        zope.component.provideUtility(
            storage, icemac.addressbook.interfaces.IOrderStorage)

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

    def test_setFieldOrder_changing_initial_order(self):
        self.entity.setFieldOrder(['dummy2', 'Field', 'dummy'])
        self.assertEqual(['dummy2', 'Field', 'dummy'],
                         self.entity.getFieldOrder())

    def test_setFieldOrder_unkown_field_names(self):
        self.entity.setFieldOrder(
            ['dummy2', 'I-do-not-exist', 'dummy', 'Field'])
        self.assertEqual(['dummy2', 'dummy', 'Field'],
                         self.entity.getFieldOrder())
        # Unknown field names are not written into storage:
        order_storage = zope.component.getUtility(
            icemac.addressbook.interfaces.IOrderStorage)
        self.assertEqual(
            ['dummy2', 'dummy', 'Field'],
            order_storage.__iter__(self.entity._order_storage_namespace))

    def test_setFieldOrder_missing_field_names(self):
        self.entity.setFieldOrder(['Field', 'dummy'])
        # getFieldOrder only contains the values set by setFieldOrder
        self.assertEqual(['Field', 'dummy'],
                         self.entity.getFieldOrder())
        # When a field name is not in the field order it gets sorted to the
        # end:
        self.assertEqual(['Field', 'dummy', 'dummy2'],
                         [x[0] for x in self.entity.getRawFields()])

    def test_getFieldOrder_initial(self):
        # The field order is initially empty:
        self.assertEqual([], self.entity.getFieldOrder())

    def test_getFieldOrder_no_utility(self):
        # When the order utility cannot be found, the field order is empty,
        # too:
        zope.component.testing.tearDown()
        self.assertEqual([], self.entity.getFieldOrder())

    def test_getFieldOrder_namespace_not_computeable(self):
        # The namespace in the order utility depends on the name of the
        # entity which itself depends on the class_name stored on the
        # entity. But this class name is optional, so the name might not be
        # computable:
        entity = icemac.addressbook.entities.Entity(u'Dummy', IDummy, None)
        self.assertEqual([], entity.getFieldOrder())

    # IEntityRead

    def test_name(self):
        self.assertEqual('IcemacAddressbookTestsTestEntityDummy',
                         self.entity.name)

    def test_name_no_class_name_set(self):
        self.assertRaises(
            ValueError, getattr,
            icemac.addressbook.entities.Entity(None, IDummy, None), "name")

    def test_getRawFields(self):
        self.entity.setFieldOrder(['dummy2', 'Field', 'dummy'])
        self.assertEqual([('dummy2', IDummy['dummy2']),
                          ('Field', self.user_field),
                          ('dummy', IDummy['dummy']),],
                         list(self.entity.getRawFields()))

    def test_getRawFields_not_sorted(self):
        # When `sorted` is false the zope.schema fields are returned first
        # (the order is defined by the order in the interface) and then the
        # user defined fields (order is undefined here.)
        self.entity.setFieldOrder(['dummy2', 'Field', 'dummy'])
        self.assertEqual([('dummy', IDummy['dummy']),
                          ('dummy2', IDummy['dummy2']),
                          ('Field', self.user_field)],
                         list(self.entity.getRawFields(sorted=False)))

    def test_getFields(self):
        self.entity.setFieldOrder(['dummy2', 'Field', 'dummy'])
        self.assertEqual([('dummy2', IDummy['dummy2']),
                          ('Field', self.schemaized_field),
                          ('dummy', IDummy['dummy'])],
                         list(self.entity.getFields()))

    def test_getFields_not_sorted(self):
        # When `sorted` is false the zope.schema fields are returned first
        # (the order is defined by the order in the interface) and then the
        # user defined fields (order is undefined here.)
        self.entity.setFieldOrder(['dummy2', 'Field', 'dummy'])
        self.assertEqual([('dummy', IDummy['dummy']),
                          ('dummy2', IDummy['dummy2']),
                          ('Field', self.schemaized_field)],
                         list(self.entity.getFields(sorted=False)))

    def test_getFieldValues(self):
        self.entity.setFieldOrder(['dummy2', 'Field', 'dummy'])
        self.assertEqual(
            [IDummy['dummy2'], self.schemaized_field, IDummy['dummy']],
            self.entity.getFieldValues())

    def test_getFieldValues_not_sorted(self):
        self.entity.setFieldOrder(['dummy2', 'Field', 'dummy'])
        self.assertEqual(
            [IDummy['dummy'], IDummy['dummy2'], self.schemaized_field],
            self.entity.getFieldValues(sorted=False))

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

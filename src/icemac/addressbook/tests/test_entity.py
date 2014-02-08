# -*- coding: utf-8 -*-
# Copyright (c) 2009-2014 Michael Howitz
# See also LICENSE.txt
import icemac.addressbook.entities
import icemac.addressbook.interfaces
import icemac.addressbook.testing
import unittest
import zope.component.testing
import zope.container.contained
import zope.container.sample
import zope.interface
import zope.schema
import zope.schema.interfaces


class IDummy(zope.interface.Interface):
    """Interface for test entity."""

    dummy = zope.schema.Text(title=u'dummy')
    dummy2 = zope.schema.Text(title=u'dummy2')


class Dummy(object):
    """Test entity."""
    zope.interface.implements(IDummy)


class TestEntity(unittest.TestCase):
    """Testing icemac.addressbook.entities.Entity."""

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
        zope.component.provideAdapter(
            icemac.addressbook.entities.user_field_to_schema_field)

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
        self.schemaized_field = zope.schema.interfaces.IField(self.user_field)

    def tearDown(self):
        zope.component.testing.tearDown()

    # IEntityWrite

    def test_addField_adds_field_to_entity(self):
        entities = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntities)
        self.assertTrue(self.user_field is entities[u'Field'])

    def test_addField_stores_entities_interface_on_field(self):
        entities = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntities)
        self.assertEqual(IDummy, entities[u'Field'].interface)

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
            order_storage.byNamespace(self.entity.order_storage_namespace))

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
                          ('dummy', IDummy['dummy'])],
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


class Test_get_bound_schema_field(unittest.TestCase):
    """Testing icemac.addressbook.entities.get_bound_schema_field()."""

    layer = icemac.addressbook.testing.ZODB_LAYER

    def callFUT(self, object, entity, field):
        from icemac.addressbook.entities import get_bound_schema_field
        return get_bound_schema_field(object, entity, field)

    def test_returns_field_if_object_provides_entity_interface(self):
        from icemac.addressbook.addressbook import address_book_entity
        import zope.schema

        ab = self.layer['addressbook']
        field = self.callFUT(ab, address_book_entity,
                             address_book_entity.getRawField('title'))
        self.assertEqual(ab, field.context)
        self.assertEqual('title', field.__name__)
        self.assertTrue(isinstance(field, zope.schema.TextLine))

    def test_looks_up_default_obj_on_obj_if_iface_not_provided_by_obj(self):
        from icemac.addressbook.address import postal_address_entity
        from icemac.addressbook.testing import create_full_person
        import zope.schema

        ab = self.layer['addressbook']
        person = create_full_person(ab, ab, u'Koch')
        field = self.callFUT(person, postal_address_entity,
                             postal_address_entity.getRawField('country'))
        self.assertEqual(person.default_postal_address, field.context)
        self.assertEqual('country', field.__name__)
        self.assertTrue(isinstance(field, zope.schema.Choice))

    def test_user_defined_fields_get_converted_to_schema_fields(self):
        from icemac.addressbook.address import phone_number_entity
        from icemac.addressbook.testing import create_full_person, create_field
        from icemac.addressbook.interfaces import IUserFieldStorage
        import zope.schema

        ab = self.layer['addressbook']
        person = create_full_person(ab, ab, u'Koch')
        create_field(ab, 'icemac.addressbook.address.PhoneNumber',
                     'Datetime', u'last call')
        field = self.callFUT(person, phone_number_entity,
                             phone_number_entity.getRawField('Field-1'))
        self.assertEqual(IUserFieldStorage(person.default_phone_number),
                         field.context)
        self.assertEqual('Field-1', field.__name__)
        self.assertTrue(isinstance(field, zope.schema.Datetime))

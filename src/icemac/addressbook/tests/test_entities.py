# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.entities
import icemac.addressbook.orderstorage
import icemac.addressbook.testing
import unittest
import zope.component.testing
import zope.interface


class IDuck(zope.interface.Interface):
    pass


class Duck(object):
    zope.interface.implements(IDuck)


class ICat(zope.interface.Interface):
    pass


class Cat(object):
    zope.interface.implements(ICat)


class IKwack(zope.interface.Interface):
    pass


class Kwack(object):
    zope.interface.implements(IKwack)


class IDog(zope.interface.Interface):
    pass


class EntitiesTests(object):

    entities_class = None

    def setUp(self):
        zope.component.testing.setUp()
        zope.component.provideAdapter(
            icemac.addressbook.entities.entity_by_name)
        zope.component.provideAdapter(
            icemac.addressbook.entities.entity_by_interface)
        self.entities = self.entities_class()
        zope.component.provideUtility(
            self.entities, icemac.addressbook.interfaces.IEntities)
        # entities
        self.cat = icemac.addressbook.entities.create_entity(
            u'Cat', ICat, Cat)
        zope.component.provideUtility(self.cat, name=self.cat.class_name)
        self.duck = icemac.addressbook.entities.create_entity(
            u'Duck', IDuck, Duck)
        zope.component.provideUtility(self.duck, name=self.duck.class_name)
        self.kwack = icemac.addressbook.entities.create_entity(
            u'Kwack', IKwack, Kwack)
        zope.component.provideUtility(
            self.kwack, name=self.kwack.class_name)
        # sort order
        order_store = icemac.addressbook.orderstorage.OrderStorage()
        order_store.add(self.cat.name, icemac.addressbook.interfaces.ENTITIES)
        order_store.add(self.kwack.name, icemac.addressbook.interfaces.ENTITIES)
        order_store.add(self.duck.name, icemac.addressbook.interfaces.ENTITIES)
        zope.component.provideUtility(
            order_store, icemac.addressbook.interfaces.IOrderStorage)
        self.order_store = order_store

    def tearDown(self):
        zope.component.testing.tearDown()

    def test_getEntities(self):
        self.assertEqual(
            sorted([self.kwack, self.duck, self.cat]),
            sorted(self.entities.getEntities()))

    def test_getEntitiesInOrder(self):
        self.assertEqual(
            [self.cat, self.kwack, self.duck],
            self.entities.getEntitiesInOrder())

    def test_getEntitiesInOrder_changed_order(self):
        self.order_store.up(
            self.duck.name, icemac.addressbook.interfaces.ENTITIES)
        self.assertEqual(
            [self.cat, self.duck, self.kwack],
            self.entities.getEntitiesInOrder())

    def test_getEntity_unknown_type(self):
        self.assertRaises(
            TypeError, icemac.addressbook.interfaces.IEntity, None)

    def test_getEntity_unknown_name(self):
        self.assertRaises(
            ValueError, icemac.addressbook.interfaces.IEntity, 'asdf')

    def test_getEntity_class_name(self):
        self.assertRaises(
            ValueError, icemac.addressbook.interfaces.IEntity,
            'icemac.addressbook.tests.test.entities.Duck')

    def test_getEntity_known_name(self):
        self.assertEqual(
            self.duck, icemac.addressbook.interfaces.IEntity(
                'IcemacAddressbookTestsTestEntitiesDuck'))

    def test_getEntity_unknown_interface(self):
        entity = icemac.addressbook.interfaces.IEntity(IDog)
        self.assert_(None is entity.title)
        self.assert_(IDog is entity.interface)
        self.assert_(None is entity.class_name)

    def test_getEntity_known_interface(self):
        self.assertEqual(
            self.kwack, icemac.addressbook.interfaces.IEntity(IKwack))

    def test_getTitle(self):
        self.assertEqual(
            u'Kwack', icemac.addressbook.interfaces.IEntity(
                'IcemacAddressbookTestsTestEntitiesKwack').title)


class TestEntities(EntitiesTests, unittest.TestCase):

    entities_class = icemac.addressbook.entities.Entities


class TestPersistentEntities(EntitiesTests, unittest.TestCase):

    entities_class = icemac.addressbook.entities.PersistentEntities


class TestEntityOrder(icemac.addressbook.testing.FunctionalTestCase):

    def setUp(self):
        import icemac.addressbook.interfaces
        import zope.component
        import zope.site.hooks

        self.old_site = zope.site.hooks.getSite()
        zope.site.hooks.setSite(
            icemac.addressbook.testing.create_addressbook(
                self.layer.getRootFolder()))

    def tearDown(self):
        zope.site.hooks.setSite(self.old_site)

    def getEntity(self, iface_name):
        import icemac.addressbook.interfaces
        return icemac.addressbook.interfaces.IEntity(
            getattr(icemac.addressbook.interfaces, iface_name))

    @property
    def entity_order(self):
        return zope.component.getUtility(
            icemac.addressbook.interfaces.IEntityOrder)

    @property
    def unknown_entity(self):
        import icemac.addressbook.entities
        import icemac.addressbook.interfaces
        return icemac.addressbook.entities.Entity(
            u'', icemac.addressbook.interfaces.IEntities,
            'icemac.addressbook.entities.Entities')

    def test_get_IPerson(self):
        self.assertEqual(1, self.entity_order.get(self.getEntity('IPerson')))

    def test_get_IKeyword(self):
        self.assertEqual(7, self.entity_order.get(self.getEntity('IKeyword')))

    def test_get_unknown_entity(self):
        self.assertRaises(KeyError, self.entity_order.get, self.unknown_entity)

    def test_isFirst_first(self):
        self.assertTrue(
            self.entity_order.isFirst(self.getEntity('IAddressBook')))

    def test_isFirst_not_first(self):
        self.assertFalse(
            self.entity_order.isFirst(self.getEntity('IPhoneNumber')))

    def test_isFirst_unknown_entity(self):
        self.assertRaises(
            KeyError, self.entity_order.isFirst, self.unknown_entity)

    def test_isLast_last(self):
        self.assertTrue(
            self.entity_order.isLast(self.getEntity('IKeyword')))

    def test_isLast_not_last(self):
        self.assertFalse(
            self.entity_order.isLast(self.getEntity('IPhoneNumber')))

    def test_isLast_unknown_entity(self):
        self.assertRaises(
            KeyError, self.entity_order.isLast, self.unknown_entity)

    def test___iter__(self):
        self.assertEqual(['IcemacAddressbookAddressbookAddressbook',
                          'IcemacAddressbookPersonPerson',
                          'IcemacAddressbookAddressPostaladdress',
                          'IcemacAddressbookAddressPhonenumber',
                          'IcemacAddressbookAddressEmailaddress',
                          'IcemacAddressbookAddressHomepageaddress',
                          'IcemacAddressbookFileFileFile',
                          'IcemacAddressbookKeywordKeyword'],
                         [x for x in self.entity_order])

    def test_up_w_o_delta(self):
        person = self.getEntity('IPerson')
        self.assertEqual(1, self.entity_order.get(person))
        self.entity_order.up(person)
        self.assertEqual(0, self.entity_order.get(person))

    def test_up_w_delta(self):
        hp = self.getEntity('IHomePageAddress')
        self.assertEqual(5, self.entity_order.get(hp))
        self.entity_order.up(hp, 3)
        self.assertEqual(2, self.entity_order.get(hp))

    def test_up_too_much(self):
        person = self.getEntity('IPerson')
        self.assertEqual(1, self.entity_order.get(person))
        self.assertRaises(ValueError, self.entity_order.up, person, 2)

    def test_down_w_o_delta(self):
        person = self.getEntity('IPerson')
        self.assertEqual(1, self.entity_order.get(person))
        self.entity_order.down(person)
        self.assertEqual(2, self.entity_order.get(person))

    def test_down_w_delta(self):
        ab = self.getEntity('IAddressBook')
        self.assertEqual(0, self.entity_order.get(ab))
        self.entity_order.down(ab, 3)
        self.assertEqual(3, self.entity_order.get(ab))

    def test_down_too_much(self):
        person = self.getEntity('IPerson')
        self.assertEqual(1, self.entity_order.get(person))
        self.assertRaises(ValueError, self.entity_order.down, person, 7)

    def test_other_address_book(self):
        # IEntityStorage always accesses the current address book as defined
        # by the setSite hook.
        import icemac.addressbook.testing
        import zope.site.hooks

        ab2 = icemac.addressbook.testing.create_addressbook(
            self.layer.getRootFolder(), name='ab2')

        person = self.getEntity('IPerson')
        self.assertEqual(1, self.entity_order.get(person))
        self.entity_order.down(person)
        self.assertEqual(2, self.entity_order.get(person))

        zope.site.hooks.setSite(ab2)
        self.assertEqual(1, self.entity_order.get(person))

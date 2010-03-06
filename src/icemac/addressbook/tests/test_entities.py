# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.entities
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

    def tearDown(self):
        zope.component.testing.tearDown()

    def test_getAllEntities(self):
        self.assertEqual(
            sorted([self.kwack, self.duck, self.cat]),
            sorted(self.entities.getAllEntities()))

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


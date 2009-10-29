# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.entities
import icemac.addressbook.interfaces
import unittest
import zope.component.testing
import zope.interface
import zope.schema


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
        self.entities = self.entities_class()
        self.cat = icemac.addressbook.entities.create_entity(
            _('Cat'), ICat, Cat)
        zope.component.provideUtility(self.cat, name=self.cat.class_name)
        self.duck = icemac.addressbook.entities.create_entity(
            _('Duck'), IDuck, Duck)
        zope.component.provideUtility(self.duck, name=self.duck.class_name)
        self.kwack = icemac.addressbook.entities.create_entity(
            _('Kwack'), IKwack, Kwack)
        zope.component.provideUtility(
            self.kwack, name=self.kwack.class_name)

    def tearDown(self):
        zope.component.testing.tearDown()

    def test_getAllEntities(self):
        self.assertEqual(
            sorted([self.kwack, self.duck, self.cat]),
            sorted(self.entities.getAllEntities()))

    def test_getEntity_unknown_type(self):
        self.assertRaises(TypeError, self.entities.getEntity, None)

    def test_getEntity_unknown_class_name(self):
        self.assertRaises(ValueError, self.entities.getEntity, 'asdf')

    def test_getEntity_known_class_name(self):
        self.assertEqual(
            self.duck, self.entities.getEntity(
                'IcemacAddressbookTestsTestEntitiesDuck'))

    def test_getEntity_unknown_interface(self):
        entity = self.entities.getEntity(IDog)
        self.assert_(None is entity.title)
        self.assert_(IDog is entity.interface)
        self.assert_(None is entity.class_name)

    def test_getEntity_known_interface(self):
        self.assertEqual(
            self.kwack, self.entities.getEntity(IKwack))

    def test_getTitle(self):
        self.assertEqual(
            _(u'Kwack'), self.entities.getTitle(
                'IcemacAddressbookTestsTestEntitiesKwack'))


class TestEntities(EntitiesTests, unittest.TestCase):

    entities_class = icemac.addressbook.entities.Entities


class TestPersistentEntities(EntitiesTests, unittest.TestCase):

    entities_class = icemac.addressbook.entities.PersistentEntities


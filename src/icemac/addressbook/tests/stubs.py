# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

"""Some entity stubs."""

import zope.interface
import zope.component
import icemac.addressbook.interfaces
import icemac.addressbook.entities


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


def setUpStubEntities(self, entities_class):
    """Create and register the stub entities."""
    self.entities = entities_class()
    zope.component.provideUtility(
        self.entities, icemac.addressbook.interfaces.IEntities)
    # entities
    self.cat = icemac.addressbook.entities.create_entity(
        u'Cat', ICat, Cat, default_attrib='default_cat')
    zope.component.provideUtility(self.cat, name=self.cat.class_name)
    self.duck = icemac.addressbook.entities.create_entity(
        u'Duck', IDuck, Duck, default_attrib='default_duck')
    zope.component.provideUtility(self.duck, name=self.duck.class_name)
    self.kwack = icemac.addressbook.entities.create_entity(
        u'Kwack', IKwack, Kwack, default_attrib='default_kwack')
    zope.component.provideUtility(self.kwack, name=self.kwack.class_name)

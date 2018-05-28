# -*- coding: utf-8 -*-
import collections
import icemac.addressbook.entities
import icemac.addressbook.interfaces
import icemac.addressbook.orderstorage
import persistent
import plone.testing.zca
import pytest
import zope.component
import zope.component.globalregistry
import zope.interface


# ready to use fixtures


@pytest.fixture(scope='function',
                params=[icemac.addressbook.entities.Entities,
                        icemac.addressbook.entities.PersistentEntities],
                ids=lambda x: x.__name__)
def stubEntities(zopeComponentTestingF, request):
    """Provide some stub entities to test the entities classes."""
    entities_util = request.param()
    zope.component.provideUtility(
        entities_util, icemac.addressbook.interfaces.IEntities)
    cat = icemac.addressbook.entities.create_entity(
        u'Cat', ICat, Cat, default_attrib='default_cat')
    zope.component.provideUtility(cat, name=cat.class_name)
    duck = icemac.addressbook.entities.create_entity(
        u'Duck', IDuck, Duck, default_attrib='default_duck')
    zope.component.provideUtility(duck, name=duck.class_name)
    kwack = icemac.addressbook.entities.create_entity(
        u'Kwack', IKwack, Kwack, default_attrib='default_kwack')
    zope.component.provideUtility(kwack, name=kwack.class_name)
    return StubEntities(entities_util, cat, duck, kwack)


@pytest.fixture(scope='function')
def stubSortOrder(stubEntities):
    """Provide an order storage for the stub entities."""
    order_store = icemac.addressbook.orderstorage.OrderStorage()
    order_store.add(
        stubEntities.cat.name, icemac.addressbook.interfaces.ENTITIES)
    order_store.add(
        stubEntities.kwack.name, icemac.addressbook.interfaces.ENTITIES)
    order_store.add(
        stubEntities.duck.name, icemac.addressbook.interfaces.ENTITIES)
    zope.component.provideUtility(
        order_store, icemac.addressbook.interfaces.IOrderStorage)
    entity_order = icemac.addressbook.entities.EntityOrder()
    zope.component.provideUtility(entity_order)
    return entity_order


@pytest.fixture(scope='function')
def entityAdapters(zopeComponentTestingF):
    """Provide some adapters to IEntity."""
    zope.component.provideAdapter(
        icemac.addressbook.entities.entity_by_name)
    zope.component.provideAdapter(
        icemac.addressbook.entities.entity_by_interface)
    zope.component.provideAdapter(
        icemac.addressbook.entities.entity_by_obj)


# Helper classes


StubEntities = collections.namedtuple(
    'StubEntities', ['entities', 'cat', 'duck', 'kwack'])


# Helper fixtures


@pytest.yield_fixture(scope='function')
def zopeComponentTestingF():
    """Set up and tear down zope.component architecture.

    Using an empty registry.
    """
    assert plone.testing.zca._REGISTRIES
    new = zope.component.globalregistry.BaseGlobalComponents(
        name='zopeComponentTestingF',
        bases=(plone.testing.zca._REGISTRIES[0],))
    plone.testing.zca.pushGlobalRegistry(new)
    yield
    current = plone.testing.zca._REGISTRIES[-1]
    current.__bases__ = (plone.testing.zca._REGISTRIES[-2],)
    plone.testing.zca.popGlobalRegistry()


# Helper classes

class IDuck(zope.interface.Interface):
    """A duck."""


@zope.interface.implementer(IDuck)
class Duck(object):
    """Duck."""


class ICat(zope.interface.Interface):
    """A cat."""


@zope.interface.implementer(ICat)
class Cat(object):
    """Cat."""


class IKwack(zope.interface.Interface):
    """A Kwack."""


@zope.interface.implementer(IKwack)
class Kwack(persistent.Persistent):
    """Kwack."""


class IDog(zope.interface.Interface):
    """A dog."""

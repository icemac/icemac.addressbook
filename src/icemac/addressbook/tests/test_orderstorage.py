# -*- coding: utf-8 -*-
from icemac.addressbook.interfaces import IOrderStorage
from icemac.addressbook.orderstorage import OrderStorage
import pytest
import zope.interface.verify


# Fixtures


@pytest.fixture('function')
def storage():
    """`OrderStorage` filled with some items."""
    storage = OrderStorage()
    storage.add('foo1', 'bar')
    storage.add('foo2', 'bar')
    storage.add('foo3', 'bar')
    storage.add('foo4', 'bar')
    storage.add('baz', 'fuz')
    return storage


def test_orderstorage__OrderStorage__1():
    """`OrderStorage` fulfills the `IOrderStorage` interface."""
    zope.interface.verify.verifyObject(IOrderStorage, OrderStorage())


def test_orderstorage__Orderstorage__add__1():
    """It allows to add objects to namespaces."""
    storage = OrderStorage()
    assert [] == list(storage.namespaces())

    storage.add('foo', 'bar')
    assert ['bar'] == list(storage.namespaces())
    assert ['foo'] == storage.byNamespace('bar')

    storage.add('foo2', 'bar2')
    assert ['bar', 'bar2'] == sorted(storage.namespaces())
    assert ['foo'] == storage.byNamespace('bar')
    assert ['foo2'] == storage.byNamespace('bar2')

    storage.add('foo2', 'bar')
    assert ['bar', 'bar2'] == sorted(storage.namespaces())
    assert ['foo', 'foo2'] == storage.byNamespace('bar')
    assert ['foo2'] == storage.byNamespace('bar2')


def test_orderstorage__Orderstorage__add__2():
    """It does not raise an error when adding an object twice."""
    storage = OrderStorage()
    storage.add('foo', 'bar')
    storage.add('foo', 'bar')
    assert ['bar'] == list(storage.namespaces())
    assert ['foo'] == storage.byNamespace('bar')


def test_orderstorage__Orderstorage__add__3():
    """Adding duplicates does not change the sort order."""
    storage = OrderStorage()
    storage.add('foo1', 'bar')
    storage.add('foo3', 'bar')
    storage.add('foo2', 'bar')
    storage.add('foo3', 'bar')
    assert ['foo1', 'foo3', 'foo2'] == storage.byNamespace('bar')


def test_orderstorage__Orderstorage__add__4():
    """It allows to add an object to different namespaces."""
    storage = OrderStorage()
    storage.add('foo', 'bar')
    storage.add('foo', 'bar2')
    assert ['bar', 'bar2'] == sorted(storage.namespaces())
    assert ['foo'] == storage.byNamespace('bar')
    assert ['foo'] == storage.byNamespace('bar2')


def test_orderstorage__Orderstorage__remove__1():
    """It allows to remove objects from the order storage."""
    storage = OrderStorage()
    storage.add('foo', 'bar')
    storage.add('foo2', 'bar2')
    storage.add('foo2', 'bar')

    storage.remove('foo', 'bar')
    assert ['bar', 'bar2'] == sorted(storage.namespaces())
    assert ['foo2'] == storage.byNamespace('bar')
    assert ['foo2'] == storage.byNamespace('bar2')

    storage.remove('foo2', 'bar2')
    assert ['bar', 'bar2'] == sorted(storage.namespaces())
    assert ['foo2'] == storage.byNamespace('bar')
    assert [] == storage.byNamespace('bar2')

    storage.remove('foo2', 'bar')
    assert ['bar', 'bar2'] == sorted(storage.namespaces())
    assert [] == storage.byNamespace('bar')
    assert [] == storage.byNamespace('bar2')


def test_orderstorage__Orderstorage__remove__2():
    """It raises `KeyError` on remove of an obj from not existing namespace."""
    storage = OrderStorage()
    storage.add('fuz', 'baz')
    with pytest.raises(KeyError):
        storage.remove('foo', 'bar')


def test_orderstorage__Orderstorage__remove__3():
    """It raises `ValueError` on remove of a not existing object."""
    storage = OrderStorage()
    storage.add('fuz', 'bar')
    with pytest.raises(ValueError):
        storage.remove('foo', 'bar')


def test_orderstorage__Orderstorage__get__1():
    """It raises a `KeyError` for a not existing namespace."""
    with pytest.raises(KeyError):
        OrderStorage().get('foo1', 'bar')


def test_orderstorage__Orderstorage__get__2():
    """It raises a `KeyError` for a not existing object."""
    storage = OrderStorage()
    storage.add('foo1', 'bar')
    with pytest.raises(KeyError):
        storage.get('foo2', 'bar')


def test_orderstorage__Orderstorage__get__3():
    """It raises a `KeyError` if the object was added to another namespace."""
    storage = OrderStorage()
    storage.add('foo1', 'baz')
    with pytest.raises(KeyError):
        storage.get('foo1', 'bar')


def test_orderstorage__Orderstorage__get__4(storage):
    """It returns the position of the item in the list."""
    storage.add('foo2', 'baz')
    assert 1 == storage.get('foo2', 'bar')
    assert 0 == storage.get('foo2', 'baz')


def test_orderstorage__Orderstorage__truncate__1():
    """It does not create a new namespace when it does not exist."""
    storage = OrderStorage()
    storage.truncate('baz')
    assert [] == sorted(storage.namespaces())


def test_orderstorage__Orderstorage__truncate__2():
    """It does only truncate the specified namespace."""
    storage = OrderStorage()
    storage.add('foo1', 'bar')
    storage.add('foo2', 'bar')
    storage.add('foo1', 'baz')
    storage.truncate('bar')
    assert [] == storage.byNamespace('bar')
    assert ['foo1'] == storage.byNamespace('baz')


def test_orderstorage__Orderstorage__up__1(storage):
    """It moves the given item one position up."""
    assert ['foo1', 'foo2', 'foo3', 'foo4'] == storage.byNamespace('bar')
    storage.up('foo3', 'bar')
    assert ['foo1', 'foo3', 'foo2', 'foo4'] == storage.byNamespace('bar')

    assert ['baz'] == storage.byNamespace('fuz')
    assert 1 == storage.get('foo3', 'bar')

    storage.up('foo3', 'bar')
    assert ['foo3', 'foo1', 'foo2', 'foo4'] == storage.byNamespace('bar')
    assert 0 == storage.get('foo3', 'bar')


def test_orderstorage__Orderstorage__up__2(storage):
    """Moving the first element up leads to a `ValueError`."""
    with pytest.raises(ValueError):
        storage.up('foo1', 'bar')


def test_orderstorage__Orderstorage__up__3(storage):
    """It moves the given item `delta` positions up."""
    storage.up('foo3', 'bar', 2)
    assert ['foo3', 'foo1', 'foo2', 'foo4'] == storage.byNamespace('bar')


def test_orderstorage__Orderstorage__up__4(storage):
    """It raises a `ValueError` when moving an element up too much."""
    with pytest.raises(ValueError):
        storage.up('foo2', 'bar', 2)


def test_orderstorage__Orderstorage__down__1(storage):
    """It moves the given item up."""
    storage.down('foo3', 'bar')
    assert ['foo1', 'foo2', 'foo4', 'foo3'] == storage.byNamespace('bar')

    assert ['baz'] == storage.byNamespace('fuz')
    assert 0 == storage.get('foo1', 'bar')

    storage.down('foo1', 'bar')
    assert ['foo2', 'foo1', 'foo4', 'foo3'] == storage.byNamespace('bar')
    assert 1 == storage.get('foo1', 'bar')


def test_orderstorage__Orderstorage__down__2(storage):
    """Moving the last element down leads to a `ValueError`."""
    with pytest.raises(ValueError):
        storage.down('foo4', 'bar')


def test_orderstorage__Orderstorage__down__3(storage):
    """It can move the given item `delta` positions down."""
    storage.down('foo2', 'bar', 2)
    assert ['foo1', 'foo3', 'foo4', 'foo2'] == storage.byNamespace('bar')


def test_orderstorage__Orderstorage__down__4(storage):
    """Moving am element down too much leads to a `ValueError`."""
    with pytest.raises(ValueError):
        storage.down('foo3', 'bar', 2)


def test_orderstorage__Orderstorage__down__5(storage):
    """If delta is 0 nothing is moved."""
    storage.down('foo2', 'bar', 0)
    assert ['foo1', 'foo2', 'foo3', 'foo4'] == storage.byNamespace('bar')


def test_orderstorage__Orderstorage__down__6(storage):
    """If delta is negative the item is not moved."""
    storage.down('foo2', 'bar', -2)
    assert ['foo1', 'foo2', 'foo3', 'foo4'] == storage.byNamespace('bar')


def test_orderstorage__Orderstorage__isFirst__1(storage):
    """It raises a `KeyError` if the item is not in the list."""
    with pytest.raises(KeyError):
        storage.isFirst('foo', 'fuz')


def test_orderstorage__Orderstorage__isFirst__2(storage):
    """It returns `False` if the item is not the first one."""
    assert not storage.isFirst('foo2', 'bar')
    assert not storage.isFirst('foo3', 'bar')
    assert not storage.isFirst('foo4', 'bar')


def test_orderstorage__Orderstorage__isFirst__3(storage):
    """It returns `True` if the item is the first one."""
    assert storage.isFirst('foo1', 'bar')
    assert storage.isFirst('baz', 'fuz')


def test_orderstorage__Orderstorage__isLast__1(storage):
    """It raises a `KeyError` if the item is not in the list."""
    with pytest.raises(KeyError):
        storage.isLast('foo', 'fuz')


def test_orderstorage__Orderstorage__isLast__2(storage):
    """It returns `False` if the item is not the last one."""
    assert not storage.isLast('foo1', 'bar')
    assert not storage.isLast('foo2', 'bar')
    assert not storage.isLast('foo3', 'bar')


def test_orderstorage__Orderstorage__isLast__3(storage):
    """It returns `True` if the item is the first one."""
    assert storage.isLast('foo4', 'bar')
    assert storage.isLast('baz', 'fuz')

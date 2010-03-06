# -*- coding: utf-8 -*-
# Copyright (c) 2010 Michael Howitz
# See also LICENSE.txt

import BTrees.OOBTree
import icemac.addressbook.interfaces
import persistent
import persistent.list
import zope.container.contained
import zope.interface


class OrderStorage(
    persistent.Persistent, zope.container.contained.Contained):
    """Storage of orders of objects."""

    zope.interface.implements(icemac.addressbook.interfaces.IOrderStorage)

    def __init__(self, *args, **kw):
        self._storage = BTrees.OOBTree.OOBTree()

    # IOrderStorageRead
    def namespaces(self):
        """Get an iterable of the known namespaces."""
        return self._storage.keys()

    def get(self, obj, namespace):
        """Get the index of the object in the list."""
        return self._storage[namespace].index(obj)

    def __iter__(self, namespace):
        """Iterate over the list of a namespace."""
        return self._storage[namespace]

    # IOrderStorageWrite
    def add(self, obj, namespace):
        """Add an object to the order for a namespace."""
        if namespace not in self._storage:
            self._storage[namespace] = persistent.list.PersistentList()
        storage = self._storage[namespace]
        if obj not in storage:
            storage.append(obj)

    def remove(self, obj, namespace):
        """Remove the object from the order of a namespace."""
        self._storage[namespace].remove(obj)

    def up(self, obj, namespace):
        """Move the object one position up in the list."""
        storage = self._storage[namespace]
        index = storage.index(obj)
        if index == 0:
            raise ValueError('%r is already the first place' % obj)
        storage[index-1:index+1] = reversed(storage[index-1:index+1])

    def down(self, obj, namespace):
        """Move the object one position down in the list."""
        storage = self._storage[namespace]
        index = storage.index(obj)
        if index == len(storage) - 1:
            raise ValueError('%r is already the last place' % obj)
        storage[index:index+2] = reversed(storage[index:index+2])

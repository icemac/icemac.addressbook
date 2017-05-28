import BTrees.OOBTree
import icemac.addressbook.interfaces
import icemac.addressbook.utils
import persistent
import persistent.list
import zope.annotation.interfaces
import zope.container.contained
import zope.interface
import zope.lifecycleevent
import zope.location


@zope.interface.implementer(zope.annotation.interfaces.IAttributeAnnotatable)
class OrderStorageList(persistent.list.PersistentList):
    """List storing orders of a single namespace.

    This list is metadata aware.
    """


@zope.interface.implementer(icemac.addressbook.interfaces.IOrderStorage)
class OrderStorage(persistent.Persistent,
                   zope.container.contained.Contained):
    """Storage of orders of objects."""

    def __init__(self, *args, **kw):
        self._storage = icemac.addressbook.utils.create_obj(
            BTrees.OOBTree.OOBTree)

    # IOrderStorageRead
    def namespaces(self):
        """Get an iterable of the known namespaces."""
        return self._storage.keys()

    def byNamespace(self, namespace):
        """Get the objects in an order namespace as a list."""
        return self._storage[namespace]

    def get(self, obj, namespace):
        """Get the index of the object in the list."""
        try:
            return self.byNamespace(namespace).index(obj)
        except ValueError:
            raise KeyError(obj)

    def isFirst(self, obj, namespace):
        """Tell whether `obj` is the first object in the list."""
        return self.get(obj, namespace) == 0

    def isLast(self, obj, namespace):
        """Tell whether `obj` is the last object in the list."""
        return ((self.get(obj, namespace) + 1) ==
                len(self.byNamespace(namespace)))

    # IOrderStorageWrite

    def add(self, obj, namespace):
        """Add an object to the order for a namespace."""
        if namespace not in self._storage:
            self._create_namespace(namespace)
        storage = self.byNamespace(namespace)
        if obj not in storage:
            storage.append(obj)
            self._modified(storage)

    def remove(self, obj, namespace):
        """Remove the object from the order of a namespace."""
        storage = self.byNamespace(namespace)
        storage.remove(obj)
        self._modified(storage)

    def truncate(self, namespace):
        """Remove all objects from the order of a namespace."""
        if namespace in self._storage:
            storage = self.byNamespace(namespace)
            # Remove all contents from storage:
            del storage[:]
            self._modified(storage)

    def up(self, obj, namespace, delta=1):
        """Move the object one position up in the list."""
        storage = self.byNamespace(namespace)
        for _ in range(delta):
            index = storage.index(obj)
            if index == 0:
                raise ValueError(
                    "Moving %r by %s positions up would move it beyond the "
                    "beginning of the list." % (obj, delta))
            storage[index - 1:index + 1] = reversed(
                storage[index - 1:index + 1])
        self._modified(storage)

    def down(self, obj, namespace, delta=1):
        """Move the object one position down in the list."""
        storage = self.byNamespace(namespace)
        for i in range(delta):
            index = storage.index(obj)
            if index == len(storage) - 1:
                raise ValueError(
                    "Moving %r by %s positions down would move it beyond the "
                    "end of the list." % (obj, delta))
            storage[index:index + 2] = reversed(storage[index:index + 2])
        self._modified(storage)

    # private

    def _create_namespace(self, namespace):
        """Create a new order namespace."""
        namespace_storage = icemac.addressbook.utils.create_obj(
            OrderStorageList)
        self._storage[namespace] = namespace_storage
        zope.location.locate(namespace_storage, self._storage, namespace)

    def _modified(self, obj):
        zope.lifecycleevent.modified(obj)

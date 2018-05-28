import zope.container.interfaces
import zope.event
import zope.lifecycleevent
import zope.traversing.api


def create_obj(class_, *args, **kw):
    """Create an object of class and fire created event."""
    obj = class_(*args)
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
    for attrib, value in kw.items():
        setattr(obj, attrib, value)
    return obj


def add(parent, obj):
    """Add `obj` to parent."""
    nc = zope.container.interfaces.INameChooser(parent)
    name = nc.chooseName('', obj)
    parent[name] = obj
    return name


def create_and_add(parent, class_, *args, **kw):
    """Create an instance of `class_`and add it to `parent`.

    *args ... used as arguments of the constructor.
    **kw ... set after creating the instance.
    """
    obj = create_obj(class_, *args, **kw)
    return add(parent, obj)


def delete(obj):
    """Delete an object from its parent."""
    name = zope.traversing.api.getName(obj)
    parent = zope.traversing.api.getParent(obj)
    del parent[name]


def iter_by_interface(container, interface):
    """Iterate a container and return only objects providing `interface`."""
    for obj in container.values():
        if interface.providedBy(obj):
            yield obj


def unique_by_attr_factory(attr_name, error_message):
    """Return a function checking `attr_name` is unique on parent."""
    def unique(obj, event=None):
        """Make sure `attr_name` is unique on obj's parent.

        May be used as handler for object events.

        """
        assert getattr(obj, '__parent__', None), \
            '%r has no true-ish __parent__.' % obj
        container = obj.__parent__
        values = [getattr(x, attr_name) for x in container.values()]
        if len(values) != len(set(values)):
            raise zope.interface.Invalid(error_message)
    return unique


def dotted_name(cls):
    """Return the dotted name of a class."""
    return "{0.__module__}.{0.__name__}".format(cls)

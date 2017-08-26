import icemac.addressbook.interfaces
import icemac.addressbook.principals.interfaces
import six
import zope.component.hooks
import zope.interface
import zope.schema.interfaces


@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def gocept_country_title(obj):
    """Title for objects from gocept.country."""
    return obj.name


@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def obj_dot_title(obj):
    """Title for an `obj` where the title is stored on `title` attribute."""
    return obj.title or u''


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def default_title(obj):
    """Default title adapter which returns `str` representation of `obj`."""
    if isinstance(obj, six.string_types):
        return obj
    return str(obj)


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(icemac.addressbook.principals.interfaces.IRoot)
def principal_root(principal):
    """Return the site root."""
    return zope.component.hooks.getSite()

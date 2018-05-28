import grokcore.component as grok
import icemac.addressbook.interfaces
import icemac.addressbook.principals.interfaces
import six
import zope.component.hooks
import zope.interface
import zope.interface.interfaces
import zope.schema.interfaces
import zope.security.proxy


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


@grok.adapter(Exception)
@grok.implementer(icemac.addressbook.interfaces.ITitle)
def exception_title(exc):
    """Special exception title to prevent lengthy Chameleon output."""
    return u"<{0.__class__.__name__}{0.args}>".format(exc)


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(icemac.addressbook.principals.interfaces.IRoot)
def principal_root(principal):
    """Return the site root."""
    return zope.component.hooks.getSite()


@grok.implementer(icemac.addressbook.interfaces.ISchemaName)
class SchemaProvider_SchemaName(grok.Adapter):
    """Adapter between ISchemaProvider and ISchemaName."""

    grok.context(icemac.addressbook.interfaces.ISchemaProvider)

    def __init__(self, context):
        # Instead of removing the security proxy I could require a ZCML class
        # definition of the usable interfaces. They are not writeable so it
        # seems too much effort to require the declaration.
        self.schema_name = unicode(
            zope.security.proxy.getObject(context.schema).getName())


@grok.implementer(icemac.addressbook.interfaces.ISchemaName)
class Interface_SchemaName(grok.Adapter):
    """Adapter between Interface and ISchemaName."""

    grok.context(zope.interface.interfaces.IInterface)

    def __init__(self, context):
        self.schema_name = unicode(context.getName())

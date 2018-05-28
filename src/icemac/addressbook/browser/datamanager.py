import icemac.addressbook.interfaces
import icemac.addressbook.metadata.interfaces
import z3c.form.datamanager
import zope.annotation.interfaces
import zope.component
import zope.schema.interfaces
import zope.security.checker


@zope.component.adapter(
    zope.annotation.interfaces.IAttributeAnnotatable,
    zope.schema.interfaces.IField)
class AnnotationField(z3c.form.datamanager.AttributeField):
    """Datamanager for data stored in annotations.

    Necessary to avoid forbidden attribute errors on annotations.  The
    code is a copy of z3c.form.datamanager.AttributeField but when the
    interface on the field is in ``self.no_security_proxy`` the
    security proxy gets removed.
    """

    no_security_proxy = (
        # interfaces those values are stored in annotations
        icemac.addressbook.interfaces.IUserFieldStorage,
        icemac.addressbook.metadata.interfaces.IEditor)

    @property
    def adapted_context(self):
        context = self.context
        if self.field.interface in self.no_security_proxy:
            context = zope.security.proxy.getObject(context)
        context = self.field.interface(context)
        return context

    def canWrite(self):
        """See z3c.form.interfaces.IDataManager"""
        if self.field.interface in self.no_security_proxy:
            # When values are stored in annotations
            # self.adapted_context is not security proxied due to
            # permission problems with annotations, so we have to
            # check whether the interaction may access __annotations__
            # on the original context.
            context = self.context
            field_name = '__annotations__'
        else:
            context = self.adapted_context
            field_name = self.field.__name__

        if isinstance(context, zope.security.checker.Proxy):
            return zope.security.checker.canWrite(context, field_name)
        return True

# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.interfaces
import z3c.form.datamanager
import zope.component
import zope.schema.interfaces
from zope.security.checker import canAccess, canWrite, Proxy


class UserDefinedField(z3c.form.datamanager.AttributeField):
    """Datamanager for user defined fields.

    Necessary to avoid forbidden attribute errors on annotations.
    The code is a copy of z3c.form.datamanager.AttributeField but when the
    interface on the field is ``IUserFieldStorage`` the security proxy gets
    removed.

    """

    zope.component.adapts(
        icemac.addressbook.interfaces.IMayHaveUserFields,
        zope.schema.interfaces.IField)

    no_security_proxy = (
        # interfaces those values are stored in annotations
        icemac.addressbook.interfaces.IUserFieldStorage,)

    @property
    def adapted_context(self):
        context = self.context
        if self.field.interface is not None:
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

        if isinstance(context, Proxy):
            return canWrite(context, field_name)
        return True

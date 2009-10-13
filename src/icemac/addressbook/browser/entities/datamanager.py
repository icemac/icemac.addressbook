# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.interfaces
import z3c.form.datamanager
import zope.component
import zope.schema.interfaces


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
        icemac.addressbook.interfaces.IUserFieldStorage,)

    @property
    def adapted_context(self):
        context = self.context
        if self.field.interface is not None:
            if self.field.interface in self.no_security_proxy:
                context = zope.security.proxy.getObject(context)
            context = self.field.interface(context)
        return context

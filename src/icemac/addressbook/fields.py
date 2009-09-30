# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import zope.interface
import icemac.addressbook.interfaces


class Fields(object):
    """Predefined and user defined schema fields of objects."""

    zope.interface.implements(icemac.addressbook.interfaces.IFields)

    def getFieldsInOrder(self, interface):
        return zope.schema.getFieldsInOrder(interface)

fields = Fields()

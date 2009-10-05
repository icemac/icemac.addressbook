# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.interfaces
import persistent
import zope.container.btree
import zope.container.contained
import zope.interface
import zope.schema.fieldproperty


class Fields(object):
    """Predefined schema fields of objects.

    Global utility as fallback when creating a new address book.
    """

    zope.interface.implements(icemac.addressbook.interfaces.IFields)

    def getFieldsInOrder(self, interface):
        return zope.schema.getFieldsInOrder(interface)

    def getFieldValuesInOrder(self, interface):
        return [field
                for name, field in zope.schema.getFieldsInOrder(interface)]


class PersistentFields(zope.container.btree.BTreeContainer, Fields):
    """Predefined and user defined schema fields of objects.

    Local utility.
    """


class Field(persistent.Persistent, zope.container.contained.Contained):
    """User defined field."""

    zope.interface.implements(icemac.addressbook.interfaces.IField)

    type = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IField['type'])
    title = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IField['title'])
    values = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IField['values'])
    order = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IField['order'])

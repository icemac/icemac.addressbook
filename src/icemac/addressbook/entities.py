# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.interfaces
import zope.interface
import persistent
import zope.container.contained
import sys

marker = object()


class Entities(object):
    "Predefined entities in the address book universe."

    zope.interface.implements(icemac.addressbook.interfaces.IEntities)

    sort_order = (
        'icemac.addressbook.person.Person', )

    # ['address_book',
    #               'person',
    #               'postal_address',
    #               'phone_number',
    #               'email_address',
    #               'home_page_address',
    #               'file',
    #               'keyword',
    #               'principal',]


    def getEntity(self, something):
        if isinstance(something, str):
            return self._get_entity_by_name(something)
        if issubclass(something, zope.interface.Interface):
            return self._get_entity_by_interface(something)
        raise TypeError("Don't know how to handle %r." % something)

    def getTitle(self, something):
        return self.getEntity(something).title

    def getAllEntities(self):
        entities = zope.component.getAllUtilitiesRegisteredFor(
            icemac.addressbook.interfaces.IEntity)
        def key(entity):
            try:
                # XXX in py25 tuple has no index method yet
                return list(self.sort_order).index(entity.class_name)
            except ValueError:
                # not in sort_order --> put to end
                return sys.maxint
        return sorted(entities, key=key)

    def _get_entity_by_name(self, name, default=marker):
        entity = zope.component.queryUtility(
            icemac.addressbook.interfaces.IEntity, name=name)
        if entity is None and default is marker:
            raise ValueError("Unknown name: %r" % name)
        return entity

    def _get_entity_by_interface(self, interface):
        for entity in self.getAllEntities():
            if entity.interface == interface:
                return entity
        # no utility found, create entity on the fly, so all even
        # not preconfigured entities can be used the same way as the
        # preconfigured ones.
        return Entity(None, interface, None)


class PersistentEntities(Entities, zope.container.btree.BTreeContainer):
    "Predefined and user defined entities in the address book."


class Entity(object):
    "An entity int the address book universe."

    zope.interface.implements(icemac.addressbook.interfaces.IEntity)

    title = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IEntity['title'])
    interface = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IEntity['interface'])
    class_name = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IEntity['class_name'])

    def __init__(self, title, interface, class_name):
        "Instantiate entity and register it as a utility."
        self.title = title
        self.interface = interface
        self.class_name = class_name
        if class_name:
            zope.component.provideUtility(self, name=class_name)

    def getFieldsInOrder(self):
        return zope.schema.getFieldsInOrder(self.interface)

    def getFieldValuesInOrder(self):
        return [
            field
            for name, field in zope.schema.getFieldsInOrder(self.interface)]



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

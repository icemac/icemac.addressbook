# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.interfaces
import persistent
import zc.sourcefactory.basic
import zope.container.contained
import zope.dottedname.resolve
import zope.interface
import zope.schema


marker = object()


class Entities(object):
    "Predefined entities in the address book universe."

    zope.interface.implements(icemac.addressbook.interfaces.IEntities)

    def getEntity(self, something):
        if isinstance(something, str):
            return self._get_entity_by_name(something)
        if issubclass(something, zope.interface.Interface):
            return self._get_entity_by_interface(something)
        raise TypeError("Don't know how to handle %r." % something)

    def getTitle(self, something):
        return self.getEntity(something).title

    def getAllEntities(self):
        return zope.component.getAllUtilitiesRegisteredFor(
            icemac.addressbook.interfaces.IEntity)

    def _get_entity_by_name(self, name, default=marker):
        entity = default
        for candidate in self.getAllEntities():
            if candidate.name == name:
                entity = candidate
                break
        if entity is marker:
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


class ChoiceFieldValuesSource(zc.sourcefactory.basic.BasicSourceFactory):
    "Source containing the values of a choice field."

    def __init__(self, values):
        super(ChoiceFieldValuesSource, self).__init__()
        self.values = values

    def getValues(self):
        return self.values

    def getTitle(self, value):
        return value


def user_field_to_schema_field(field):
    """Convert a user defined field (IField) into a zope.schema field."""
    if field.type == 'Choice':
        schema_field = zope.schema.Choice(
            title=field.title, required=False,
            source=ChoiceFieldValuesSource(field.values))
    else:
        schema_field = getattr(zope.schema, field.type)(
            title=field.title, required=False)
    schema_field.__name__ = str(field.__name__)
    schema_field.interface = (
        icemac.addressbook.interfaces.IUserFieldStorage)
    return schema_field


class FakeObject(object):
    "We need an instance to provide an interface for the `getAdapters` call."


class Entity(object):
    "An entity int the address book universe."
    # Use `create_entity` factory for easier usage.

    zope.interface.implements(icemac.addressbook.interfaces.IEntity)

    title = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IEntity['title'])
    interface = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IEntity['interface'])
    class_name = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IEntity['class_name'])

    def __init__(self, title, interface, class_name):
        # To create an entity, use `create_entity` factory (see below) which
        # also does the ZCA set up.
        self.title = title
        self.interface = interface
        self.class_name = class_name
        # getRawFields needs an instance which provides the interface to
        # look up the user defined fields which are named adapters
        self._fake_object = FakeObject()
        zope.interface.directlyProvides(self._fake_object, self.interface)

    @property
    def name(self):
        parts = self.class_name.replace('_', '.').split('.')
        return ''.join(x.capitalize() for x in parts)

    def getRawFields(self):
        for name, field in zope.schema.getFieldsInOrder(self.interface):
            yield name, field
        # self._fake_object is needed here as the interfaces provided by the
        # objects are used in the look up
        adapters = zope.component.getAdapters(
            (self, self._fake_object), icemac.addressbook.interfaces.IField)
        for name, field in adapters:
            yield str(field.__name__), field

    def getFieldsInOrder(self):
        for name, field in self.getRawFields():
            if icemac.addressbook.interfaces.IField.providedBy(field):
                yield name, user_field_to_schema_field(field)
            else:
                yield name, field

    def getFieldValuesInOrder(self):
        return [field for name, field in self.getFieldsInOrder()]

    def getField(self, field_name):
        return dict(self.getFieldsInOrder())[field_name]

    def getClass(self):
        if self.class_name:
            return zope.dottedname.resolve.resolve(self.class_name)
        raise ValueError("class_name is not set.")


class Field(persistent.Persistent, zope.container.contained.Contained):
    """User defined field."""

    zope.interface.implements(icemac.addressbook.interfaces.IField)

    type = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IField['type'])
    title = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IField['title'])
    values = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IField['values'])
    notes = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IField['notes'])


class FieldAdapterFactory(persistent.Persistent):
    "Factory to register a field as an adapter."

    def __init__(self, field):
        self._field = field

    def __call__(self, *args):
        return self._field


def store_and_register_field(field, entity):
    "Store a `field` in the ZODB and register it for an `entity`."
    # store in entities utility
    parent = zope.component.getUtility(icemac.addressbook.interfaces.IEntities)
    name = icemac.addressbook.utils.add(parent, field)
    # register as adapter
    sm = zope.site.hooks.getSiteManager()
    sm.registerAdapter(
        FieldAdapterFactory(field),
        provided=icemac.addressbook.interfaces.IField,
        required=(icemac.addressbook.interfaces.IEntity, entity.interface),
        name=name)
    return name


class FieldStorage(persistent.Persistent):
    """Storage for field values in annotations."""
    zope.component.adapts(
        icemac.addressbook.interfaces.IMayHaveUserFields)
    zope.interface.implements(
        icemac.addressbook.interfaces.IUserFieldStorage)

    def __getattr__(self, attrib):
        # We have no default values on the class nor we might know them.
        if not attrib.startswith('__'):
            return self.__dict__.get(attrib, None)
        raise AttributeError(attrib)


field_storage = zope.annotation.factory(
    FieldStorage, key='icemac.userfield.storage')


def create_entity(title, interface, class_):
    "Factory to create an entity and to the ZCA set up."
    class_name = '%s.%s' % (class_.__module__, class_.__name__)
    entity = Entity(title, interface, class_name)
    zope.interface.classImplements(
        class_, icemac.addressbook.interfaces.IMayHaveUserFields)
    return entity

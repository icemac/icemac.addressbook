# -*- coding: utf-8 -*-
import grokcore.component
import icemac.addressbook.interfaces
import persistent
import persistent.interfaces
import zc.sourcefactory.basic
import zope.container.contained
import zope.dottedname.resolve
import zope.interface.interfaces
import zope.schema
import zope.schema.fieldproperty
import zope.schema.interfaces
import zope.security.proxy
import zope.traversing.api


MAIN_ENTITIES_NAME_SUFFIXES = [
    'person.Person',
    'address.PostalAddress',
    'address.PhoneNumber',
    'address.EMailAddress',
    'address.HomePageAddress',
]


def sorted_entities(entities):
    """Return the entities sorted as defined in IEntityOrder."""
    order = zope.component.getUtility(
        icemac.addressbook.interfaces.IEntityOrder)
    order = list(order)
    return sorted(entities, key=lambda x: order.index(x.name))


class Entities(object):
    """Predefined entities in the address book universe."""

    zope.interface.implements(icemac.addressbook.interfaces.IEntities)

    def getEntities(self, sorted=True):
        """Get an iterable of all known entities."""
        entities = zope.component.getAllUtilitiesRegisteredFor(
            icemac.addressbook.interfaces.IEntity)
        if sorted:
            entities = sorted_entities(entities)
        return entities

    def getMainEntities(self, sorted=True):
        """Get an iterable of the most important entities."""
        entities = [
            zope.component.getUtility(
                icemac.addressbook.interfaces.IEntity,
                name='icemac.addressbook.' + suffix)
            for suffix in MAIN_ENTITIES_NAME_SUFFIXES]
        if sorted:
            entities = sorted_entities(entities)
        return entities


class PersistentEntities(Entities, zope.container.btree.BTreeContainer):
    """Predefined entities and user defined fields in the address book."""


@zope.component.adapter(basestring)
@zope.interface.implementer(icemac.addressbook.interfaces.IEntity)
def entity_by_name(name):
    """Adapt Entity.name (not Entity.class_name!) to entity."""
    entities = zope.component.getUtility(
        icemac.addressbook.interfaces.IEntities).getEntities(sorted=False)
    for candidate in entities:
        if candidate.name == name:
            return candidate
    raise ValueError("Unknown name: %r" % name)


@zope.component.adapter(zope.interface.interfaces.IInterface)
@zope.interface.implementer(icemac.addressbook.interfaces.IEntity)
def entity_by_interface(interface):
    """Adapt an interface to its entity."""
    entities = zope.component.getUtility(
        icemac.addressbook.interfaces.IEntities).getEntities(sorted=False)
    for entity in entities:
        if entity.interface == interface:
            return entity
    # no entity found, create one on the fly, so all entities (even not
    # preconfigured ones) can be used the same way.
    return Entity(None, interface, None)


@zope.component.adapter(persistent.interfaces.IPersistent)
@zope.interface.implementer(icemac.addressbook.interfaces.IEntity)
def entity_by_obj(obj):
    """Adapt instance to entity."""
    entities = zope.component.getUtility(
        icemac.addressbook.interfaces.IEntities).getEntities(sorted=False)
    for candidate in entities:
        if candidate.interface.providedBy(obj):
            return candidate
    raise ValueError("Unknown obj: %r" % obj)


class EntityOrder(object):
    """Global entity order utility."""

    zope.interface.implements(icemac.addressbook.interfaces.IEntityOrder)

    @property
    def order_storage(self):
        return zope.component.getUtility(
            icemac.addressbook.interfaces.IOrderStorage)

    def _get_entity_name(self, entity):
        try:
            return entity.name
        except ValueError:
            raise KeyError('Entity %r in not known in entity order.' % entity)

    def get(self, entity):
        """Get the index of the entity in the entity order."""
        return self.order_storage.get(
            self._get_entity_name(entity),
            icemac.addressbook.interfaces.ENTITIES)

    def isFirst(self, entity):
        """Tell whether `entity` comes first in the entity order."""
        return self.order_storage.isFirst(
            self._get_entity_name(entity),
            icemac.addressbook.interfaces.ENTITIES)

    def isLast(self, entity):
        """Tell whether `entity` comes last in the entity order."""
        return self.order_storage.isLast(
            self._get_entity_name(entity),
            icemac.addressbook.interfaces.ENTITIES)

    def __iter__(self):
        """Iterate over the entities sorted by order."""
        return iter(self.order_storage.byNamespace(
            icemac.addressbook.interfaces.ENTITIES))

    def up(self, entity, delta=1):
        """Move the entity one position up in the entity order."""
        return self.order_storage.up(
            self._get_entity_name(entity),
            icemac.addressbook.interfaces.ENTITIES, delta)

    def down(self, entity, delta=1):
        """Move the entity one position down in the entity order."""
        return self.order_storage.down(
            self._get_entity_name(entity),
            icemac.addressbook.interfaces.ENTITIES, delta)


class ChoiceFieldValuesSource(zc.sourcefactory.basic.BasicSourceFactory):
    """Source containing the values of a choice field."""

    def __init__(self, values):
        super(ChoiceFieldValuesSource, self).__init__()
        self.values = values

    def getValues(self):
        return self.values

    def getTitle(self, value):
        return value


@grokcore.component.adapter(icemac.addressbook.interfaces.IField)
@grokcore.component.implementer(zope.schema.interfaces.IField)
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


def index(key, list, default):
    """Index of `key` in `list` but `default` when it is not in `list`."""
    try:
        return list.index(key)
    except ValueError:
        return default


def sorted_fields(fields, field_order):
    """Return the fields sorted by their index in the `field_order`.

    Fields which are not in the `field_order` are sorted to the end
    accordingly to their position in the `fields` list.

    """
    raw_field_order = [x[0] for x in fields]
    return sorted(
        fields,
        key=lambda (name, field): index(
            name, field_order, 100000 + raw_field_order.index(name)))


class FakeObject(object):
    """Provider for an interface for the `getAdapters` call."""


class Entity(object):
    """An entity int the address book universe."""

    # Use `create_entity` factory for easier usage.
    # Caution: This class is only a base class, in most cases you will use
    #          EditableEntity (see below).

    zope.interface.implements(icemac.addressbook.interfaces.IEntity)
    zope.schema.fieldproperty.createFieldProperties(
        icemac.addressbook.interfaces.IEntityRead)

    def __init__(self, title, interface, class_name, **kw):
        # To create an entity, use `create_entity` factory (see below) which
        # also does the ZCA set up.
        self.title = title
        self.interface = interface
        self.class_name = class_name
        # _get_raw_fields_unordered needs an instance which provides the
        # interface to look up the user defined fields which are named
        # adapters:
        self._fake_object = FakeObject()
        zope.interface.directlyProvides(self._fake_object, self.interface)
        # Additional keyword arguments are stored as tagged values
        self._tagged_values = kw

    @property
    def name(self):
        """Uniqe name of the entity which only contains letters."""
        if not self.class_name:
            raise ValueError(
                "Entity has no `class_name` set, so `name` cannot be computed."
            )
        parts = self.class_name.replace('_', '.').split('.')
        return ''.join(x.capitalize() for x in parts)

    @property
    def tagged_values(self):
        """Dict of tagged values of the entity."""
        return self._tagged_values.copy()

    @property
    def order_storage_namespace(self):
        """Get the name space used in the order storage."""
        return '%s%s' % (
            icemac.addressbook.interfaces.FIELD_NS_PREFIX, self.name)

    def getRawFields(self, sorted=True):
        """Get (name, field) tuples of the schema fields on the entity.

        When `sorted` is true the fields are sorted using the field order.

        Returns static (zope.schema) and user defined (IField) fields.

        """
        raw_fields = self._get_raw_fields_unordered()
        if not sorted:
            return raw_fields
        return sorted_fields(list(raw_fields), self.getFieldOrder())

    def getFields(self, sorted=True):
        """Get (name, field) tuples of the schema fields on the entity.

        When `sorted` is true the fields are sorted using the field order.

        Converts user defined fields (see IField) into zope.schema fields.

        """
        for name, field in self.getRawFields(sorted=sorted):
            yield name, zope.schema.interfaces.IField(field)

    def getFieldValues(self, sorted=True):
        """Get list of the schema fields on the entity.

        When `sorted` is true the fields are sorted using the field order.

        Converts user defined fields (see IField) into zope.schema fields.

        """
        return [field for name, field in self.getFields(sorted=sorted)]

    def getRawField(self, field_name):
        """Get a field by its name."""
        return dict(self.getRawFields(sorted=False))[field_name]

    def getField(self, field_name):
        """Get a zope.schema field by its name."""
        return dict(self.getFields(sorted=False))[field_name]

    def getClass(self):
        """Get the class object for `self.class_name`."""
        if self.class_name:
            return zope.dottedname.resolve.resolve(self.class_name)
        raise ValueError("class_name is not set.")

    def getFieldOrder(self):
        """Get the ordered names of the fields."""
        order_storage = zope.component.queryUtility(
            icemac.addressbook.interfaces.IOrderStorage)
        try:
            return order_storage.byNamespace(self.order_storage_namespace)
        except (KeyError, ValueError, AttributeError):
            # Either the order_storage is None or the namespace cannot be
            # computed or it is unknown, so we can't order the fields.
            return []

    # IEntityWrite

    def addField(self, field):
        """Add a user defined field to the entity."""
        # The field needs to be stored in the entities utility:
        parent = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntities)
        name = icemac.addressbook.utils.add(parent, field)
        # The field needs to be an adapter:
        sm = zope.site.hooks.getSiteManager()
        sm.registerAdapter(
            FieldAdapterFactory(field),
            provided=icemac.addressbook.interfaces.IField,
            required=(icemac.addressbook.interfaces.IEntity, self.interface),
            name=name)
        field.interface = self.interface
        return name

    def removeField(self, field):
        """Remove a user defined field from the entity."""
        sm = zope.site.hooks.getSiteManager()
        # The field no longer is allowed to be an adapter:
        sm.unregisterAdapter(
            provided=icemac.addressbook.interfaces.IField,
            required=(icemac.addressbook.interfaces.IEntity, self.interface),
            name=zope.traversing.api.getName(field))
        field.interface = None
        # The field needs to be removed from the entities utility:
        icemac.addressbook.utils.delete(field)

    def setFieldOrder(self, field_names):
        """Update the order of the fields like in `field_names`."""
        order_storage = zope.component.getUtility(
            icemac.addressbook.interfaces.IOrderStorage)
        existing_field_names = [x[0] for x in self._get_raw_fields_unordered()]
        ns = self.order_storage_namespace
        # Removing exising contents of namespace in order storage while
        # creating the namespace when it does not yet exist
        order_storage.truncate(ns)
        for name in field_names:
            if name not in existing_field_names:
                # We do not allow to write arbitrary data here:
                continue
            order_storage.add(name, ns)

    # private

    def _get_raw_fields_unordered(self):
        """Get the raw fields not ordered."""
        for name, field in zope.schema.getFieldsInOrder(self.interface):
            yield name, field
        # self._fake_object is needed here as the interfaces provided by the
        # objects are used in the look-up
        adapters = zope.component.getAdapters(
            (self, self._fake_object), icemac.addressbook.interfaces.IField)
        for name, field in adapters:
            yield str(field.__name__), field


class EditableEntity(Entity):
    """Special entity which is editable.

    This means that new fields can be added and the fields can be sorted.
    """

    zope.interface.implementsOnly(
        icemac.addressbook.interfaces.IEditableEntity)


def create_entity(title, interface, class_, **kw):
    """Factory to create an editable entity and to the ZCA set up."""
    class_name = '%s.%s' % (class_.__module__, class_.__name__)
    entity = EditableEntity(title, interface, class_name, **kw)
    zope.interface.classImplements(
        class_, icemac.addressbook.interfaces.IMayHaveUserFields)
    return entity


class Field(persistent.Persistent, zope.container.contained.Contained):
    """User defined field."""

    zope.interface.implements(icemac.addressbook.interfaces.IField)
    zope.schema.fieldproperty.createFieldProperties(
        icemac.addressbook.interfaces.IField)
    interface = None


class FieldAdapterFactory(persistent.Persistent):
    """Factory to register a field as an adapter."""

    def __init__(self, field):
        self._field = field

    def __call__(self, *args):
        return self._field


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
        # Cloning a person tries to access __reduce_ex__ and
        # __reduce__ which are not in __dict__. It is expeced that
        # they are either methods or not existing, so None is no valid
        # return value.
        raise AttributeError(attrib)


field_storage = zope.annotation.factory(
    FieldStorage, key='icemac.userfield.storage')


def get_bound_schema_field(obj, entity, field, default_attrib_fallback=True):
    """Return a bound zope.schema field for `entity` and `field` on `obj`.

    If `default_attrib_fallback` is true and `obj` does not provide the
    `entity` interface fall back to the `default_attrib`

    """
    if default_attrib_fallback and not entity.interface.providedBy(obj):
        # If the entity is for another object, we expect to find the entity
        # on a default_attrib.
        obj = getattr(obj, entity.tagged_values['default_attrib'])
    if icemac.addressbook.interfaces.IField.providedBy(field):
        # User defined fields need to be adapted. Additionally security
        # proxy must be removed as otherwise access fails. This might be a
        # security hole if access to this function is not properly
        # protected, but there is no other way.
        obj = zope.security.proxy.getObject(obj)
        obj = icemac.addressbook.interfaces.IUserFieldStorage(obj)
        field = zope.schema.interfaces.IField(field)
    return field.bind(obj)

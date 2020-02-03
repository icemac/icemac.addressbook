# -*- coding: utf-8 -*-
from icemac.addressbook.interfaces import MIN_SUPPORTED_DATE
from icemac.addressbook.utils import dotted_name
import grokcore.component as grok
import icemac.addressbook.interfaces
import persistent
import persistent.interfaces
import persistent.mapping
import six
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


@zope.interface.implementer(icemac.addressbook.interfaces.IEntities)
class Entities(object):
    """Predefined entities in the address book universe."""

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


@zope.component.adapter(six.string_types[0])
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


@grok.adapter(icemac.addressbook.interfaces.IField)
@grok.implementer(icemac.addressbook.interfaces.IEntity)
def entity_for_field(field):
    """Adapt a field to its entity."""
    return icemac.addressbook.interfaces.IEntity(field.interface, None)


@zope.interface.implementer(icemac.addressbook.interfaces.IEntityOrder)
class EntityOrder(object):
    """Global entity order utility."""

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


@grok.adapter(icemac.addressbook.interfaces.IField)
@grok.implementer(zope.schema.interfaces.IField)
def user_field_to_schema_field(field):
    """Convert a user defined field (IField) into a zope.schema field."""
    kwargs = dict(title=field.title, description=field.notes, required=False)
    if field.type == 'Choice':
        kwargs['source'] = ChoiceFieldValuesSource(field.values)
    elif field.type == 'Date':
        kwargs['min'] = MIN_SUPPORTED_DATE
    schema_field = getattr(zope.schema, field.type)(**kwargs)
    schema_field.__name__ = str(field.__name__)
    schema_field.interface = icemac.addressbook.interfaces.IUserFieldStorage
    return schema_field


def fields_sort_key_factory(fields, field_order):
    """Return a function to sort `fields` by the `field_order`."""
    raw_field_order = [x[0] for x in fields]

    def key(key):
        name, field = key
        try:
            return field_order.index(name)
        except ValueError:
            return 100000 + raw_field_order.index(name)
    return key


def sorted_fields(fields, field_order):
    """Return the fields sorted by their index in the `field_order`.

    Fields which are not in the `field_order` are sorted to the end
    accordingly to their position in the `fields` list.

    """
    return sorted(fields, key=fields_sort_key_factory(fields, field_order))


class FakeObject(object):
    """Provider for an interface for the `getAdapters` call."""


@zope.interface.implementer(icemac.addressbook.interfaces.IEntity)
class Entity(object):
    """An entity int the address book universe."""

    # Use `create_entity` factory for easier usage.
    # Caution: This class is only a base class, in most cases you will use
    #          EditableEntity (see below).

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
        if sorted:
            raw_fields = sorted_fields(list(raw_fields), self.getFieldOrder())
        return raw_fields

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
        sm = zope.component.hooks.getSiteManager()
        sm.registerAdapter(
            FieldAdapterFactory(field),
            provided=icemac.addressbook.interfaces.IField,
            required=(icemac.addressbook.interfaces.IEntity, self.interface),
            name=name)
        field.interface = self.interface
        return name

    def removeField(self, field):
        """Remove a user defined field from the entity."""
        sm = zope.component.hooks.getSiteManager()
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


@zope.interface.implementer_only(icemac.addressbook.interfaces.IEditableEntity)
class EditableEntity(Entity):
    """Special entity which is editable.

    This means that new fields can be added and the fields can be sorted.
    """


def create_entity(title, interface, class_, **kw):
    """Factory to create an editable entity and to the ZCA set up."""
    entity = EditableEntity(title, interface, dotted_name(class_), **kw)
    zope.interface.classImplements(
        class_, icemac.addressbook.interfaces.IMayHaveUserFields)
    return entity


@zope.interface.implementer(icemac.addressbook.interfaces.IField)
class Field(persistent.Persistent, zope.container.contained.Contained):
    """User defined field."""

    zope.schema.fieldproperty.createFieldProperties(
        icemac.addressbook.interfaces.IField)
    interface = None


class FieldAdapterFactory(persistent.Persistent):
    """Factory to register a field as an adapter."""

    def __init__(self, field):
        self._field = field

    def __call__(self, *args):
        return self._field


@zope.component.adapter(icemac.addressbook.interfaces.IMayHaveUserFields)
@zope.interface.implementer(icemac.addressbook.interfaces.IUserFieldStorage)
class FieldStorage(persistent.Persistent):
    """Storage for field values in annotations."""

    def __getattr__(self, attrib):
        """Get a attribute value stored in `self.__dict__`."""
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


@zope.component.adapter(zope.site.interfaces.IRootFolder)
@zope.interface.implementer(icemac.addressbook.interfaces.IFieldCustomization)
class NoFieldCustomization(object):
    """No custom data for schema field to be shown in the UI.

    This happens on the root folder where no user customization is possible.
    """

    DEFAULT_ATTRIB_MAP = {
        'label': 'title',
        'description': 'description',
    }

    def __init__(self, context):
        pass

    def set_value(self, field, kind, label):
        """Cannot set a new value."""
        raise NotImplementedError

    def get_value(self, field, kind):
        """Cannot get a stored value."""
        raise KeyError

    def query_value(self, field, kind):
        """Get the default value as there is no custom one."""
        return self.default_value(field, kind)

    def default_value(self, field, kind):
        """Get the default value for the field."""
        unsecure_field = zope.security.proxy.getObject(field)
        attr = self.DEFAULT_ATTRIB_MAP[kind]
        return getattr(unsecure_field, attr)


@zope.component.adapter(icemac.addressbook.interfaces.IAddressBook)
@zope.interface.implementer(icemac.addressbook.interfaces.IFieldCustomization)
class FieldCustomization(persistent.mapping.PersistentMapping,
                         NoFieldCustomization):
    """Custom data for schema field to be shown in the UI."""

    def set_value(self, field, kind, value):
        """Set a new value of type kind for the given field.

        kind … either u'label' or u'description'

        Use `None` as value of `label` to delete the stored custom value.
        """
        if value is None:
            try:
                del self[self._key(field, kind)]
            except KeyError:
                pass
        else:
            self[self._key(field, kind)] = value

    def get_value(self, field, kind):
        """Get the stored value of type kind for the field.

        kind … either u'label' or u'description'

        If no custom value is stored, a KeyError is raised.
        """
        return self[self._key(field, kind)]

    def query_value(self, field, kind):
        """Get the stored value of type kind for the field.

        If no custom value is stored, return the default value.
        """
        try:
            return self.get_value(field, kind)
        except KeyError:
            return self.default_value(field, kind)

    @staticmethod
    def _key(field, kind):
        """Compute the key for a field and a kind."""
        assert kind in ('label', 'description')
        unsecure_field = zope.security.proxy.getObject(field)
        iface = unsecure_field.interface
        if iface is None:
            iface_dotted_name = "None"
        else:
            iface_dotted_name = dotted_name(iface)
        return u"{}:{}:{}".format(iface_dotted_name, field.__name__, kind)


field_customization = zope.annotation.factory(
    FieldCustomization, key='icemac.predefined_field.customization')


def get_field_label(field):
    """Get the possibly customized label of the field."""
    address_book = icemac.addressbook.interfaces.IAddressBook(None)
    customization = icemac.addressbook.interfaces.IFieldCustomization(
        address_book)
    return customization.query_value(field, u'label')

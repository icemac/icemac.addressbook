from icemac.addressbook.address import phone_number_entity
from icemac.addressbook.address import postal_address_entity
from icemac.addressbook.addressbook import address_book_entity
from icemac.addressbook.entities import Entities, PersistentEntities, Field
from icemac.addressbook.entities import Entity, get_bound_schema_field
from icemac.addressbook.entities import EntityOrder
from icemac.addressbook.entities import FieldCustomization
from icemac.addressbook.entities import NoFieldCustomization
from icemac.addressbook.interfaces import IAddressBook, IHomePageAddress
from icemac.addressbook.interfaces import IEntities, IEntityOrder, IEntity
from icemac.addressbook.interfaces import IField, IOrderStorage
from icemac.addressbook.interfaces import IFieldCustomization
from icemac.addressbook.interfaces import IPhoneNumber, IPerson, IKeyword
from icemac.addressbook.interfaces import IUserFieldStorage
from icemac.addressbook.testing import pyTestStackDemoStorage
from icemac.addressbook.tests.conftest import IDog, IKwack, Kwack
import persistent
import pytest
import zope.component
import zope.component.hooks
import zope.interface
import zope.interface.verify
import zope.schema
import zope.schema.interfaces


# Constants

DEFAULT_ORDER = [u'person',
                 u'postal address',
                 u'phone number',
                 u'e-mail address',
                 u'home page address']


# Fixtures

@pytest.fixture(scope='function')
def entityOrder(address_book):
    """Get the entity order utility."""
    return zope.component.getUtility(IEntityOrder)


@pytest.fixture(scope='module')
def unknownEntity():
    """Get an entity which is not known in the address book."""
    return Entity(u'', IEntities, 'icemac.addressbook.entities.Entities')


@pytest.fixture(scope='function')
def minimalEntity(address_book):
    """Get an entity which is not registered in the address book."""
    return IEntity(IEntities)


@pytest.fixture(scope='function')
def field():
    """Get a user defined field."""
    field = Field()
    field.type = 'TextLine'
    return field


@pytest.fixture(scope='function')
def schemaized_field(field):
    """Get a user defined field adapted to a `zope.schema` field."""
    return zope.schema.interfaces.IField(field)


@pytest.fixture(scope='function')
def entity():
    """Get a custom entity."""
    return Entity(
        u'Dummy', IDummy, 'icemac.addressbook.tests.test_entities.Dummy')


@pytest.fixture(scope='function')
def entity_with_field(address_book, entity, field):
    """Get a custom entity with a user defined field."""
    entity.addField(field)
    return entity


@pytest.fixture(scope='function')
def entities(address_book):
    """Get the entities utility."""
    return zope.component.getUtility(IEntities)


@pytest.yield_fixture(scope='function')
def root_folder(zodbS):
    """Get the root folder of the ZODB."""
    for connection in pyTestStackDemoStorage(zodbS, 'root_folder'):
        yield connection.rootFolder


# Helper classes


class IDummy(zope.interface.Interface):
    """Interface for test entity."""

    dummy = zope.schema.Text(title=u'dummy')
    dummy2 = zope.schema.Text(title=u'dummy2')


@zope.interface.implementer(IDummy)
class Dummy(object):
    """Test entity."""


# Helper functions

def getMainEntities_titles(sorted):
    """Return the entities titles when calling `getMainEntities()`."""
    entities = zope.component.getUtility(IEntities)
    return [x.title for x in entities.getMainEntities(sorted=sorted)]


# Tests


def test_entities__Entities__1():
    """`Entities` fulfills the `IEntities` interface."""
    zope.interface.verify.verifyObject(IEntities, Entities())


def test_entities__PersistentEntities__1():
    """`PersistentEntities` fulfills the `IEntities` interface."""
    zope.interface.verify.verifyObject(IEntities, PersistentEntities())


def test_entities__EntityOrder__1():
    """`EntityOrder` fulfills the `IEntityOrder` interface."""
    zope.interface.verify.verifyObject(IEntityOrder, EntityOrder())


def test_entities__Field__1():
    """`Field` fulfills the `IField` interface."""
    zope.interface.verify.verifyObject(IField, Field())


def test_entities__Entity__1():
    """`Entity` fulfills the `IEntity` interface."""
    entity = Entity(None, IEntity, 'Entity')
    zope.interface.verify.verifyObject(IEntity, entity)


def test_entities__getEntities__1(stubSortOrder, stubEntities):
    """`(Persistent)Entities.getEntities()` returns entities sorted.

    The sort order is defined in the sort order storage.
    """
    e = stubEntities
    assert [e.cat, e.kwack, e.duck] == e.entities.getEntities()


def test_entities__getEntities__2(stubEntities):
    """`(Persistent)Entities.getEntities()` might return entities unsorted."""
    e = stubEntities
    assert (sorted([e.kwack, e.duck, e.cat]) ==
            sorted(e.entities.getEntities(sorted=False)))


def test_entities__getEntities__3(stubSortOrder, stubEntities):
    """`(Persistent)Entities.getEntities()` respects changes in sort order."""
    e = stubEntities
    stubSortOrder.up(e.duck)
    assert [e.cat, e.duck, e.kwack] == e.entities.getEntities()


def test_entities__PersistentEntities__getMainEntities__1(address_book):
    """By default the result of `getMainEntities()` is sort independent."""
    assert DEFAULT_ORDER == getMainEntities_titles(True)
    assert DEFAULT_ORDER == getMainEntities_titles(False)


def test_entities__PersistentEntities__getMainEntities__2(entityOrder):
    """`getMainEntities()` respects a changed sort order."""
    entityOrder.up(IEntity(IPhoneNumber))
    assert ([u'person',
             u'phone number',
             u'postal address',
             u'e-mail address',
             u'home page address'] == getMainEntities_titles(True))
    # The unordered variant still returns the default order:
    assert DEFAULT_ORDER == getMainEntities_titles(False)


def test_entities__EntityOrder__get__1(entityOrder):
    """`get()` returns the position of the entity."""
    assert 1 == entityOrder.get(IEntity(IPerson))
    assert 8 == entityOrder.get(IEntity(IKeyword))


def test_entities__EntityOrder__get__2(entityOrder, unknownEntity):
    """`get()` raises a KeyError if entity is not known to the sort order."""
    with pytest.raises(KeyError):
        entityOrder.get(unknownEntity)


def test_entities__EntityOrder__get__3(entityOrder, minimalEntity):
    """`get()` raises a KeyError if the entity has no name."""
    with pytest.raises(KeyError):
        entityOrder.get(minimalEntity)


def test_entities__EntityOrder__get__4(entityOrder, AddressBookFactory):
    """It accesses the address book in `zope.component.hooks.site`."""
    other_address_book = AddressBookFactory('other_address_book')
    # Changes in an address book ...
    person = IEntity(IPerson)
    assert 1 == entityOrder.get(person)
    entityOrder.down(person)
    assert 2 == entityOrder.get(person)
    # ... are not reflected in another address book:
    with zope.component.hooks.site(other_address_book):
        assert 1 == entityOrder.get(person)


def test_entities__EntityOrder__get__5(entityOrder):
    """`get()` raises a ComponentLookupError if no site is set."""
    person = IEntity(IPerson)
    with zope.component.hooks.site(None):
        with pytest.raises(zope.component.ComponentLookupError):
            entityOrder.get(person)


def test_entities__EntityOrder__isFirst__1(entityOrder):
    """`isFirst()` returns `True` for the first entity."""
    assert entityOrder.isFirst(IEntity(IAddressBook))


def test_entities__EntityOrder__isFirst__2(entityOrder):
    """`isFirst()` returns `False` for an entity which is not the first."""
    assert not entityOrder.isFirst(IEntity(IPhoneNumber))


def test_entities__EntityOrder__isFirst__3(entityOrder, unknownEntity):
    """`isFirst()` raises KeyError if entity is not known to the sort order."""
    with pytest.raises(KeyError):
        entityOrder.isFirst(unknownEntity)


def test_entities__EntityOrder__isFirst__4(entityOrder, minimalEntity):
    """`isFirst()` raises KeyError if the entity has no name."""
    with pytest.raises(KeyError):
        entityOrder.isFirst(minimalEntity)


def test_entities__EntityOrder__isLast__1(entityOrder):
    """`isLast()` returns `True` for the first entity."""
    assert entityOrder.isLast(IEntity(IKeyword))


def test_entities__EntityOrder__isLast__2(entityOrder):
    """`isLast()` returns `False` for an entity which is not the first."""
    assert not entityOrder.isLast(IEntity(IPhoneNumber))


def test_entities__EntityOrder__isLast__3(entityOrder, unknownEntity):
    """`isLast()` raises KeyError if entity is not known to the sort order."""
    with pytest.raises(KeyError):
        entityOrder.isLast(unknownEntity)


def test_entities__EntityOrder__isLast__4(entityOrder, minimalEntity):
    """`isLast()` raises KeyError if the entity has no name."""
    with pytest.raises(KeyError):
        entityOrder.isLast(minimalEntity)


def test_entities__EntityOrder____iter____1(entityOrder):
    """It is iterable, returning entity names."""
    assert ([
        'IcemacAddressbookAddressbookAddressbook',
        'IcemacAddressbookPersonPerson',
        'IcemacAddressbookPersonPersondefaults',
        'IcemacAddressbookAddressPostaladdress',
        'IcemacAddressbookAddressPhonenumber',
        'IcemacAddressbookAddressEmailaddress',
        'IcemacAddressbookAddressHomepageaddress',
        'IcemacAddressbookFileFileFile',
        'IcemacAddressbookKeywordKeyword',
    ] == list(iter(entityOrder)))


def test_entities__EntityOrder__up__1(entityOrder):
    """`up()` moved one position up."""
    person = IEntity(IPerson)
    assert 1 == entityOrder.get(person)
    entityOrder.up(person)
    assert 0 == entityOrder.get(person)


def test_entities__EntityOrder__up__2(entityOrder):
    """`up(n)` moves n positions up."""
    hp = IEntity(IHomePageAddress)
    assert 6 == entityOrder.get(hp)
    entityOrder.up(hp, 3)
    assert 3 == entityOrder.get(hp)


def test_entities__EntityOrder__up__3(entityOrder):
    """If the delta is too big when calling `up()` a ValueError is raised."""
    person = IEntity(IPerson)
    assert 1 == entityOrder.get(person)
    with pytest.raises(ValueError):
        entityOrder.up(person, 2)


def test_entities__EntityOrder__down__1(entityOrder):
    """`down()` moved one position down."""
    person = IEntity(IPerson)
    assert 1 == entityOrder.get(person)
    entityOrder.down(person)
    assert 2 == entityOrder.get(person)


def test_entities__EntityOrder__down__2(entityOrder):
    """`down(n)` moves n positions down."""
    ab = IEntity(IAddressBook)
    assert 0 == entityOrder.get(ab)
    entityOrder.down(ab, 3)
    assert 3 == entityOrder.get(ab)


def test_entities__EntityOrder__down__3(entityOrder):
    """If the delta is too big when calling `down()` a ValueError is raised."""
    person = IEntity(IPerson)
    assert 1 == entityOrder.get(person)
    with pytest.raises(ValueError):
        entityOrder.down(person, 8)


def test_entities__entity_by_name__1(stubEntities, entityAdapters):
    """`entity_by_name` raises a `ValueError` if string name is unknown."""
    with pytest.raises(ValueError):
        IEntity('asdf')


def test_entities__entity_by_name__2(stubEntities, entityAdapters):
    """`entity_by_name` raises a `ValueError` if unicode name is unknown."""
    with pytest.raises(ValueError):
        IEntity(u'asdf')


def test_entities__entity_by_name__3(stubEntities, entityAdapters):
    """`entity_by_name` raises a `ValueError` if class name is used."""
    with pytest.raises(ValueError):
        IEntity('icemac.addressbook.tests.stubs.Duck')


def test_entities__entity_by_name__4(stubEntities, entityAdapters):
    """`entity_by_name` raises a `ValueError` if class name is used."""
    with pytest.raises(ValueError):
        IEntity('icemac.addressbook.tests.conftest.Duck')


def test_entities__entity_by_name__5(stubEntities, entityAdapters):
    """`entity_by_name` adapts from string entity name."""
    assert stubEntities.duck == IEntity('IcemacAddressbookTestsConftestDuck')


def test_entities__entity_by_name__6(stubEntities, entityAdapters):
    """`entity_by_name` adapts from unicode entity name."""
    assert stubEntities.duck == IEntity(u'IcemacAddressbookTestsConftestDuck')


def test_entities__entity_by_interface__1(stubEntities, entityAdapters):
    """`entity_by_interface` returns a minimal entity for unknown interface."""
    entity = IEntity(IDog)
    assert None is entity.title
    assert IDog is entity.interface
    assert None is entity.class_name


def test_entities__entity_by_interface__2(stubEntities, entityAdapters):
    """`entity_by_interface` returns the entity for a known interface."""
    assert stubEntities.kwack == IEntity(IKwack)


def test_entities__entity_by_obj__1(stubEntities, entityAdapters):
    """`entity_by_obj` raises a ValueError for an unknown instance."""
    obj = persistent.Persistent()
    with pytest.raises(ValueError):
        IEntity(obj)


def test_entities__entity_by_obj__2(stubEntities, entityAdapters):
    """`entity_by_obj` returns the instance for a known instance."""
    assert stubEntities.kwack == IEntity(Kwack())


def test_entities__Entity__addField__1(entities, entity, field):
    """It adds a field to an entity."""
    entity.addField(field)
    assert ['Field-1'] == list(entities.keys())
    assert field is entities[u'Field-1']


def test_entities__Entity__addField__2(entities, entity, field):
    """It stores the interface of the entity on the field."""
    entity.addField(field)
    assert IDummy == entities[u'Field-1'].interface


def test_entities__Entity__addField__3(address_book, field):
    """It registers an adapter for the field."""
    address_book_entity.addField(field)
    adapted_entity = zope.component.getMultiAdapter(
        (address_book_entity, address_book), IField, name=u'Field-1')
    assert field is adapted_entity


def test_entities__entity_for_field__1(address_book, field):
    """It adapts a field to its entity."""
    address_book_entity.addField(field)

    adapted_field = IEntity(field)
    assert address_book_entity == adapted_field


def test_entities__Entity__removeField__1(entities, entity_with_field, field):
    """It removes a field from an entity."""
    assert field in entities.values()
    entity_with_field.removeField(field)
    assert field not in entities.values()


def test_entities__Entity__removeField__2(entity_with_field, field):
    """It removes the interface of the entity from the field."""
    entity_with_field.removeField(field)
    assert field.interface is None


def test_entities__Entity__removeField__3(entity_with_field, field):
    """It removes the adapter registrations for the field."""
    entity_with_field.removeField(field)
    assert None is zope.component.queryMultiAdapter(
        (entity, Dummy()), IField, name=u'Field')
    assert None is IEntity(field, None)


def test_entities__Entity__setFieldOrder__1(entity_with_field, field):
    """It changes the initial (empty) order."""
    assert [] == entity_with_field.getFieldOrder()
    entity_with_field.setFieldOrder(['dummy2', field.__name__, 'dummy'])
    assert (['dummy2', field.__name__, 'dummy'] ==
            entity_with_field.getFieldOrder())


def test_entities__Entity__setFieldOrder__2(entity_with_field):
    """It ignores unknown field names and does not store them."""
    entity = entity_with_field
    entity.setFieldOrder(['dummy2', 'I-do-not-exist', 'dummy'])
    assert ['dummy2', 'dummy'] == entity.getFieldOrder()
    # Unknown field names are not written into storage:
    order_storage = zope.component.getUtility(IOrderStorage)
    assert (['dummy2', 'dummy'] ==
            order_storage.byNamespace(entity.order_storage_namespace))


def test_entities__Entity__getFieldOrder__1(entity):
    """It returns the initially emtpy field order."""
    assert [] == entity.getFieldOrder()


def test_entities__Entity__getFieldOrder__2(entity_with_field, field):
    """It only contains the values set by `setFieldOrder`."""
    entity = entity_with_field
    entity.setFieldOrder([field.__name__, 'dummy'])
    assert [field.__name__, 'dummy'] == entity.getFieldOrder()


def test_entities__Entity__getFieldOrder__3(address_book):
    """It returns `[]` if the namespace cannot be computed."""
    # The namespace in the order utility depends on the name of the
    # entity which itself depends on the class_name stored on the
    # entity. But this class name is optional, so the name might not be
    # computable:
    entity = Entity(u'Dummy', IDummy, None)
    assert [] == entity.getFieldOrder()


def test_entities__Entity__name__1(entity):
    """`name` is the name of the entity containing the module path."""
    assert 'IcemacAddressbookTestsTestEntitiesDummy' == entity.name


def test_entities__Entity__name__2(address_book):
    """`name` raises a ValueError if no class name is set."""
    entity = Entity(None, IDummy, None)
    with pytest.raises(ValueError):
        entity.name


def test_entities__Entity__getRawFields__1(entity_with_field, field):
    """`getRawFields` sorts fields missing in sort order to the end."""
    entity = entity_with_field
    entity.setFieldOrder([field.__name__, 'dummy'])
    assert ([field.__name__, 'dummy', 'dummy2'] ==
            [x[0] for x in entity.getRawFields()])


def test_entities__Entity__getRawFields__2(entity_with_field, field):
    """`getRawFields` returns the fields sorted by the field order."""
    entity = entity_with_field
    entity.setFieldOrder(['dummy2', field.__name__, 'dummy'])
    assert ([('dummy2', IDummy['dummy2']),
             (field.__name__, field),
             ('dummy', IDummy['dummy'])] == list(entity.getRawFields()))


def test_entities__Entity__getRawFields__3(entity_with_field, field):
    """`getRawFields` is able to return the fields unsorted (default order).

    When `sorted` is `False` the `zope.schema` fields are returned first (the
    order is defined by the order in the interface) and than the user defined
    fields (order is undefined here.)
    """
    entity = entity_with_field
    entity.setFieldOrder(['dummy2', 'Field', 'dummy'])
    assert ([('dummy', IDummy['dummy']),
             ('dummy2', IDummy['dummy2']),
             (field.__name__, field)] ==
            list(entity.getRawFields(sorted=False)))


def test_entities__Entity__getFields__1(entity_with_field, schemaized_field):
    """`getFields` returns all fields as `zope.schema` in order."""
    entity = entity_with_field
    entity.setFieldOrder(['dummy2', schemaized_field.__name__, 'dummy'])
    assert ([('dummy2', IDummy['dummy2']),
             (schemaized_field.__name__, schemaized_field),
             ('dummy', IDummy['dummy'])] == list(entity.getFields()))


def test_entities__Entity__getFields__2(entity_with_field, schemaized_field):
    """`geFields` is able to return the fields unsorted (default order).

    When `sorted` is `False` the `zope.schema` fields are returned first (the
    order is defined by the order in the interface) and then the user defined
    fields (order is undefined here.)
    """
    entity = entity_with_field
    entity.setFieldOrder(['dummy2', schemaized_field.__name__, 'dummy'])
    assert ([('dummy', IDummy['dummy']),
             ('dummy2', IDummy['dummy2']),
             (schemaized_field.__name__, schemaized_field)] ==
            list(entity.getFields(sorted=False)))


def test_entities__Entity__getFieldValues__1(
        entity_with_field, schemaized_field):
    """`getFieldValues` returns all fields as `zope.schema` in order."""
    entity = entity_with_field
    entity.setFieldOrder(['dummy2', schemaized_field.__name__, 'dummy'])
    assert ([IDummy['dummy2'], schemaized_field, IDummy['dummy']] ==
            entity.getFieldValues())


def test_entities__Entity__getFieldValues__2(
        entity_with_field, schemaized_field):
    """`getFieldValues` is able to return the fields unsorted (default order).

    When `sorted` is `False` the `zope.schema` fields are returned first (the
    order is defined by the order in the interface) and then the user defined
    fields (order is undefined here.)
    """
    entity = entity_with_field
    entity.setFieldOrder(['dummy2', schemaized_field.__name__, 'dummy'])
    assert ([IDummy['dummy'], IDummy['dummy2'], schemaized_field] ==
            entity.getFieldValues(sorted=False))


def test_entities__Entity__getField__1(entity):
    """`getField` raises a `KeyError` for an unknown field name."""
    with pytest.raises(KeyError):
        entity.getField('asdf')


def test_entities__Entity__getField__2(entity):
    """`getField` can return a `zope.schema` field."""
    assert IDummy['dummy2'] == entity.getField('dummy2')


def test_entities__Entity__getField__3(entity_with_field, schemaized_field):
    """`getField` can return a user defined field as `zope.schema` field."""
    assert (schemaized_field ==
            entity_with_field.getField(schemaized_field.__name__))


def test_entities__Entity__getRawField__1(entity):
    """`getRawField` raises a `KeyError` for an unknown field name."""
    with pytest.raises(KeyError):
        entity.getRawField('asdf')


def test_entities__Entity__getRawField__2(entity):
    """`getRawField` can return a `zope.schema` field."""
    assert IDummy['dummy2'] == entity.getRawField('dummy2')


def test_entities__Entity__getRawField__3(entity_with_field, field):
    """`getRawField` can return a user defined field."""
    assert field == entity_with_field.getRawField(field.__name__)


def test_entities__Entity__getClass__1(entity):
    """`getClass` returns the class object associated with the entity."""
    assert Dummy == entity.getClass()


def test_entities__Entity__getClass__2():
    """`getClass` raises a `ValueError` if no `class_name` is set."""
    e = Entity(None, IDummy, None)
    with pytest.raises(ValueError):
        e.getClass()


def test_entities__Entity__tagged_values__1():
    """`tagged_values` is a dict of the kwargs used during entity __init__."""
    e = Entity(u'Dummy', IDummy, 'Dummy', a=1, b='asdf')
    assert dict(a=1, b='asdf') == e.tagged_values


def test_entities__Entity__tagged_values__2():
    """`tagged_values` is actually a copy of the kwargs dict.

    Tagged values not modifiable by modifying the returned dict.
    """
    e = Entity(u'Dummy', IDummy, 'Dummy', a=1, b='asdf')
    e.tagged_values['a'] = 2
    assert dict(a=1, b='asdf') == e.tagged_values


def test_entities__get_bound_schema_field__1(address_book):
    """It returns the schema field if the obj provides the entity interface."""
    field = get_bound_schema_field(address_book, address_book_entity,
                                   address_book_entity.getRawField('title'))
    assert address_book == field.context
    assert 'title' == field.__name__
    assert isinstance(field, zope.schema.TextLine)


def test_entities__get_bound_schema_field__2(address_book, FullPersonFactory):
    """It looks up the default obj on obj if iface is not provided by obj."""
    person = FullPersonFactory(address_book, u'Koch')
    field = get_bound_schema_field(
        person, postal_address_entity,
        postal_address_entity.getRawField('country'))
    assert person.default_postal_address == field.context
    assert 'country' == field.__name__
    assert isinstance(field, zope.schema.Choice)


def test_entities__get_bound_schema_field__3(address_book, FullPersonFactory):
    """It binds field to obj if `default_attrib_fallback` is `False`.

    Additional condition: The interface is not provided by obj.
    """
    person = FullPersonFactory(address_book, u'Koch')
    field = get_bound_schema_field(
        person, postal_address_entity,
        postal_address_entity.getRawField('country'),
        default_attrib_fallback=False)
    assert person == field.context


def test_entities__get_bound_schema_field__4(
        address_book, FullPersonFactory, FieldFactory):
    """It returns a user defined field as a `zope.schema` field."""
    person = FullPersonFactory(address_book, u'Koch')
    FieldFactory(address_book, IPhoneNumber, 'Datetime', u'last call',
                 notes=u'using a phone')
    field = get_bound_schema_field(
        person, phone_number_entity,
        phone_number_entity.getRawField('Field-1'))
    assert IUserFieldStorage(person.default_phone_number) == field.context
    assert 'Field-1' == field.__name__
    assert 'using a phone' == field.description
    assert isinstance(field, zope.schema.Datetime)


def test_entities__NoFieldCustomization__1(root_folder):
    """It implements the IFieldCustomization interface."""
    nfc = IFieldCustomization(root_folder)
    assert isinstance(nfc, NoFieldCustomization)
    assert zope.interface.verify.verifyObject(IFieldCustomization, nfc)


def test_entities__NoFieldCustomization__get_value__1(root_folder):
    """It raises a KeyError."""
    nfc = IFieldCustomization(root_folder)
    with pytest.raises(KeyError):
        nfc.get_value(IAddressBook['time_zone'], 'label')


def test_entities__NoFieldCustomization__default_value__1(root_folder):
    """It returns the title of the field (default value)."""
    nfc = IFieldCustomization(root_folder)
    assert u'Time zone' == nfc.default_value(
        IAddressBook['time_zone'], 'label')


@pytest.mark.parametrize(
    'kind, result',
    ((u'label', u'Time zone'),
     (u'description', u'Fallback in case a user has not set up his personal'
                      u' time zone in the preferences.')))
def test_entities__NoFieldCustomization__query_value__1(
        root_folder, kind, result):
    """It returns the default value."""
    nfc = IFieldCustomization(root_folder)
    assert result == nfc.query_value(IAddressBook['time_zone'], kind)


def test_entities__NoFieldCustomization__set_value__1(root_folder):
    """It is not implemented."""
    nfc = IFieldCustomization(root_folder)
    with pytest.raises(NotImplementedError):
        nfc.set_value(IAddressBook['time_zone'], u'label', u'foo')


def test_entities__FieldCustomization__1(address_book):
    """It implements the IFieldCustomization interface."""
    fc = IFieldCustomization(address_book)
    assert isinstance(fc, FieldCustomization)
    assert zope.interface.verify.verifyObject(IFieldCustomization, fc)


def test_entities__FieldCustomization__get_value__1(address_book):
    """It raises a KeyError if no custom value is stored."""
    fc = IFieldCustomization(address_book)
    with pytest.raises(KeyError):
        fc.get_value(IAddressBook['time_zone'], 'label')


def test_entities__FieldCustomization__get_value__2(address_book):
    """It raises a KeyError if the field does not belong to an interface."""
    fc = IFieldCustomization(address_book)
    field = zope.schema.Text()
    with pytest.raises(KeyError):
        fc.get_value(field, 'label')


def test_entities__FieldCustomization__default_value__1(address_book):
    """It returns the title of the field (default value)."""
    fc = IFieldCustomization(address_book)
    assert u'Time zone' == fc.default_value(IAddressBook['time_zone'], 'label')


@pytest.mark.parametrize(
    'kind, result',
    ((u'label', u'Time zone'),
     (u'description', u'Fallback in case a user has not set up his personal'
                      u' time zone in the preferences.')))
def test_entities__FieldCustomization__query_value__1(
        address_book, kind, result):
    """It returns the default value if no custom label is stored."""
    fc = IFieldCustomization(address_book)
    assert result == fc.query_value(IAddressBook['time_zone'], kind)


def test_entities__FieldCustomization__set_value__1(address_book):
    """It stores the given custom value."""
    fc = IFieldCustomization(address_book)
    field = IAddressBook['time_zone']
    fc.set_value(field, u'label', u'Default time zone value 123')
    assert u'Default time zone value 123' == fc.get_value(field, 'label')
    assert u'Default time zone value 123' == fc.query_value(field, 'label')


def test_entities__FieldCustomization__set_value__2(address_book):
    """Storing `None` removes the custom value."""
    fc = IFieldCustomization(address_book)
    field = IAddressBook['time_zone']
    fc.set_value(field, u'label', u'Default time zone value 123')
    fc.set_value(field, u'label', None)
    with pytest.raises(KeyError):
        fc.get_value(field, 'label')


def test_entities__FieldCustomization__set_value__3(address_book):
    """It does not break on storing `None` with no custom value stored."""
    fc = IFieldCustomization(address_book)
    field = IAddressBook['time_zone']
    fc.set_value(field, u'label', None)
    with pytest.raises(KeyError):
        fc.get_value(field, 'label')

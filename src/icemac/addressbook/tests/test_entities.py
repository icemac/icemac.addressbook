
import icemac.addressbook.entities
import icemac.addressbook.orderstorage
import icemac.addressbook.testing
import plone.testing.zca
import unittest
import zope.component.testing


class EntitiesTests(object):

    entities_class = None

    def setUp(self):
        from icemac.addressbook.tests.stubs import setUpStubEntities
        zope.component.testing.setUp()
        setUpStubEntities(self, self.entities_class)
        # sort order
        order_store = icemac.addressbook.orderstorage.OrderStorage()
        order_store.add(self.cat.name, icemac.addressbook.interfaces.ENTITIES)
        order_store.add(
            self.kwack.name, icemac.addressbook.interfaces.ENTITIES)
        order_store.add(self.duck.name, icemac.addressbook.interfaces.ENTITIES)
        zope.component.provideUtility(
            order_store, icemac.addressbook.interfaces.IOrderStorage)
        self.entity_order = icemac.addressbook.entities.EntityOrder()
        zope.component.provideUtility(self.entity_order)

    def tearDown(self):
        zope.component.testing.tearDown()

    def test_getEntities(self):
        self.assertEqual(
            sorted([self.kwack, self.duck, self.cat]),
            sorted(self.entities.getEntities(sorted=False)))

    def test_getEntities_sorted(self):
        self.assertEqual(
            [self.cat, self.kwack, self.duck],
            self.entities.getEntities())

    def test_getEntitiesInOrder_changed_order(self):
        self.entity_order.up(self.duck)
        self.assertEqual(
            [self.cat, self.duck, self.kwack],
            self.entities.getEntities())


class TestEntities(EntitiesTests, unittest.TestCase):

    entities_class = icemac.addressbook.entities.Entities


class TestPersistentEntities(EntitiesTests, unittest.TestCase):

    entities_class = icemac.addressbook.entities.PersistentEntities


class TestEntities_getMainEntities(unittest.TestCase):

    layer = icemac.addressbook.testing.ZODB_LAYER

    def callFUT(self, sorted):
        import zope.component
        import icemac.addressbook.interfaces

        entities = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntities)
        return [x.title for x in entities.getMainEntities(sorted=sorted)]

    DEFAULT_ORDER = [u'person', u'postal address', u'phone number',
                     u'e-mail address', u'home page address']

    def test_default_order(self):
        # With unchanged sort order both variants return the same order:
        self.assertEqual(self.DEFAULT_ORDER, self.callFUT(True))
        self.assertEqual(self.DEFAULT_ORDER, self.callFUT(False))

    def test_changed_order(self):
        import zope.component
        import icemac.addressbook.interfaces

        order = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntityOrder)
        phone_number = icemac.addressbook.interfaces.IEntity(
            icemac.addressbook.interfaces.IPhoneNumber)
        order.up(phone_number)
        self.assertEqual(
            [u'person', u'phone number', u'postal address', u'e-mail address',
             u'home page address'],
            self.callFUT(True))
        # Unordered variant still returns the default order:
        self.assertEqual(self.DEFAULT_ORDER, self.callFUT(False))


class TestEntityOrder(unittest.TestCase):

    layer = icemac.addressbook.testing.ZODB_LAYER

    def getEntity(self, iface_name):
        import icemac.addressbook.interfaces
        return icemac.addressbook.interfaces.IEntity(
            getattr(icemac.addressbook.interfaces, iface_name))

    @property
    def entity_order(self):
        return zope.component.getUtility(
            icemac.addressbook.interfaces.IEntityOrder)

    @property
    def unknown_entity(self):
        import icemac.addressbook.entities
        import icemac.addressbook.interfaces
        return icemac.addressbook.entities.Entity(
            u'', icemac.addressbook.interfaces.IEntities,
            'icemac.addressbook.entities.Entities')

    @property
    def minimal_entity(self):
        import icemac.addressbook.interfaces
        return icemac.addressbook.interfaces.IEntity(
            icemac.addressbook.interfaces.IEntities)

    def test_get_IPerson(self):
        self.assertEqual(1, self.entity_order.get(self.getEntity('IPerson')))

    def test_get_IKeyword(self):
        self.assertEqual(8, self.entity_order.get(self.getEntity('IKeyword')))

    def test_get_unknown_entity(self):
        self.assertRaises(KeyError, self.entity_order.get, self.unknown_entity)

    def test_get_minimal_entity(self):
        # When the entity has no name, a KeyError is raised, too.
        self.assertRaises(KeyError, self.entity_order.get, self.minimal_entity)

    def test_isFirst_first(self):
        self.assertTrue(
            self.entity_order.isFirst(self.getEntity('IAddressBook')))

    def test_isFirst_not_first(self):
        self.assertFalse(
            self.entity_order.isFirst(self.getEntity('IPhoneNumber')))

    def test_isFirst_unknown_entity(self):
        self.assertRaises(
            KeyError, self.entity_order.isFirst, self.unknown_entity)

    def test_isFirst_minimal_entity(self):
        self.assertRaises(
            KeyError, self.entity_order.isFirst, self.minimal_entity)

    def test_isLast_last(self):
        self.assertTrue(
            self.entity_order.isLast(self.getEntity('IKeyword')))

    def test_isLast_not_last(self):
        self.assertFalse(
            self.entity_order.isLast(self.getEntity('IPhoneNumber')))

    def test_isLast_unknown_entity(self):
        self.assertRaises(
            KeyError, self.entity_order.isLast, self.unknown_entity)

    def test_isLast_minimal_entity(self):
        self.assertRaises(
            KeyError, self.entity_order.isLast, self.minimal_entity)

    def test___iter__(self):
        self.assertEqual(['IcemacAddressbookAddressbookAddressbook',
                          'IcemacAddressbookPersonPerson',
                          'IcemacAddressbookPersonPersondefaults',
                          'IcemacAddressbookAddressPostaladdress',
                          'IcemacAddressbookAddressPhonenumber',
                          'IcemacAddressbookAddressEmailaddress',
                          'IcemacAddressbookAddressHomepageaddress',
                          'IcemacAddressbookFileFileFile',
                          'IcemacAddressbookKeywordKeyword'],
                         [x for x in self.entity_order])

    def test_up_w_o_delta(self):
        person = self.getEntity('IPerson')
        self.assertEqual(1, self.entity_order.get(person))
        self.entity_order.up(person)
        self.assertEqual(0, self.entity_order.get(person))

    def test_up_w_delta(self):
        hp = self.getEntity('IHomePageAddress')
        self.assertEqual(6, self.entity_order.get(hp))
        self.entity_order.up(hp, 3)
        self.assertEqual(3, self.entity_order.get(hp))

    def test_up_too_much(self):
        person = self.getEntity('IPerson')
        self.assertEqual(1, self.entity_order.get(person))
        self.assertRaises(ValueError, self.entity_order.up, person, 2)

    def test_down_w_o_delta(self):
        person = self.getEntity('IPerson')
        self.assertEqual(1, self.entity_order.get(person))
        self.entity_order.down(person)
        self.assertEqual(2, self.entity_order.get(person))

    def test_down_w_delta(self):
        ab = self.getEntity('IAddressBook')
        self.assertEqual(0, self.entity_order.get(ab))
        self.entity_order.down(ab, 3)
        self.assertEqual(3, self.entity_order.get(ab))

    def test_down_too_much(self):
        person = self.getEntity('IPerson')
        self.assertEqual(1, self.entity_order.get(person))
        self.assertRaises(ValueError, self.entity_order.down, person, 8)

    def test_other_address_book(self):
        # IEntityStorage always accesses the current address book as defined
        # by the setSite hook.
        import icemac.addressbook.testing
        import zope.site.hooks

        ab2 = icemac.addressbook.testing.create_addressbook(
            'ab2', parent=self.layer['rootFolder'])

        person = self.getEntity('IPerson')
        self.assertEqual(1, self.entity_order.get(person))
        self.entity_order.down(person)
        self.assertEqual(2, self.entity_order.get(person))

        zope.site.hooks.setSite(ab2)
        self.assertEqual(1, self.entity_order.get(person))

    def test_outside_address_book(self):
        # Outside an address book a ComponentLookupError is raised:
        import zope.component
        import zope.site.hooks

        zope.site.hooks.setSite(None)
        self.assertRaises(
            zope.component.ComponentLookupError,
            self.entity_order.get, self.getEntity('IPerson'))


class TestEntityAdapters(unittest.TestCase):

    layer = plone.testing.zca.UNIT_TESTING

    def setUp(self):
        from icemac.addressbook.tests.stubs import setUpStubEntities
        setUpStubEntities(self, icemac.addressbook.entities.Entities)
        zope.component.provideAdapter(
            icemac.addressbook.entities.entity_by_name)
        zope.component.provideAdapter(
            icemac.addressbook.entities.entity_by_interface)
        zope.component.provideAdapter(
            icemac.addressbook.entities.entity_by_obj)

    # no adapter
    def test_unknown_type(self):
        self.assertRaises(
            TypeError, icemac.addressbook.interfaces.IEntity, None)

    # adaption from string
    def test_unknown_string_name(self):
        self.assertRaises(
            ValueError, icemac.addressbook.interfaces.IEntity, 'asdf')

    # adaption from unicode
    def test_unknown_unicode_name(self):
        self.assertRaises(
            ValueError, icemac.addressbook.interfaces.IEntity, u'asdf')

    def test_class_name(self):
        self.assertRaises(
            ValueError, icemac.addressbook.interfaces.IEntity,
            'icemac.addressbook.tests.stubs.Duck')

    # adaption from string
    def test_known_string_name(self):
        self.assertEqual(
            self.duck, icemac.addressbook.interfaces.IEntity(
                'IcemacAddressbookTestsStubsDuck'))

    # adaption from unicode
    def test_known_unicode_name(self):
        self.assertEqual(
            self.duck, icemac.addressbook.interfaces.IEntity(
                u'IcemacAddressbookTestsStubsDuck'))

    # adaption from interface
    def test_unknown_interface(self):
        from icemac.addressbook.tests.stubs import IDog
        entity = icemac.addressbook.interfaces.IEntity(IDog)
        self.assert_(None is entity.title)
        self.assert_(IDog is entity.interface)
        self.assert_(None is entity.class_name)

    def test_known_interface(self):
        from icemac.addressbook.tests.stubs import IKwack
        self.assertEqual(
            self.kwack, icemac.addressbook.interfaces.IEntity(IKwack))

    # adaption from object
    def test_unknown_object(self):
        from persistent import Persistent
        obj = Persistent()
        self.assertRaises(
            ValueError, icemac.addressbook.interfaces.IEntity, obj)

    def test_known_object(self):
        from icemac.addressbook.tests.stubs import Kwack
        self.assertEqual(
            self.kwack, icemac.addressbook.interfaces.IEntity(Kwack()))

    # title
    def test_getTitle(self):
        self.assertEqual(
            u'Kwack', icemac.addressbook.interfaces.IEntity(
                'IcemacAddressbookTestsStubsKwack').title)

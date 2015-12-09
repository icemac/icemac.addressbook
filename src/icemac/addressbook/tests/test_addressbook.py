import icemac.addressbook.addressbook
import icemac.addressbook.interfaces
import icemac.addressbook.testing
import unittest
import zope.authentication.interfaces
import zope.catalog.interfaces
import zope.intid.interfaces
import zope.location.interfaces
import zope.pluggableauth.interfaces


class TestAddressbook(unittest.TestCase,
                      icemac.addressbook.testing.InstallationAssertions):

    layer = icemac.addressbook.testing.ZODB_LAYER

    def check_addressbook(self, ab):
        self.assertTrue(zope.location.interfaces.ISite.providedBy(ab))
        self.assertAttribute(
            ab, 'keywords', icemac.addressbook.interfaces.IKeywords)
        self.assertAttribute(
            ab, 'principals',
            zope.pluggableauth.interfaces.IAuthenticatorPlugin,
            name=u'icemac.addressbook.principals')
        self.assertAttribute(
            ab, 'entities',
            icemac.addressbook.interfaces.IEntities)
        self.assertAttribute(
            ab, 'orders',
            icemac.addressbook.interfaces.IOrderStorage)
        self.assertLocalUtility(ab, zope.intid.interfaces.IIntIds)
        self.assertLocalUtility(ab, zope.catalog.interfaces.ICatalog)
        self.assertLocalUtility(
            ab, zope.authentication.interfaces.IAuthentication)

    def setUp(self):
        super(TestAddressbook, self).setUp()
        self.ab = self.layer['addressbook']

    def test_create(self):
        self.check_addressbook(self.ab)

    def test_recall_create_infrastructure(self):
        icemac.addressbook.addressbook.create_address_book_infrastructure(
            self.ab)
        self.check_addressbook(self.ab)

    def test___repr___no___name__(self):
        self.assertEqual("<AddressBook None (None)>",
                         repr(icemac.addressbook.addressbook.AddressBook()))

    def test___repr___no_title(self):
        self.assertEqual("<AddressBook u'ab' (None)>", repr(self.ab))

    def test___repr__(self):
        self.ab.title = u'My address book'
        self.assertEqual("<AddressBook u'ab' (u'My address book')>",
                         repr(self.ab))

    def test_entity_order_is_created_initially(self):
        from icemac.addressbook.interfaces import ENTITIES
        self.assertEqual(
            ['IcemacAddressbookAddressbookAddressbook',
             'IcemacAddressbookPersonPerson',
             'IcemacAddressbookPersonPersondefaults',
             'IcemacAddressbookAddressPostaladdress',
             'IcemacAddressbookAddressPhonenumber',
             'IcemacAddressbookAddressEmailaddress',
             'IcemacAddressbookAddressHomepageaddress',
             'IcemacAddressbookFileFileFile',
             'IcemacAddressbookKeywordKeyword'],
            self.ab.orders.byNamespace(ENTITIES))

    def test_only_entity_order_is_created_initially(self):
        from icemac.addressbook.interfaces import ENTITIES
        self.assertEqual([ENTITIES], list(self.ab.orders.namespaces()))


class GetAddressBookTests(unittest.TestCase):
    """Testing ..addressbook.get_address_book."""

    layer = icemac.addressbook.testing.ZODB_LAYER

    def test_returns_current_addressbook(self):
        from icemac.addressbook.interfaces import IAddressBook
        self.assertEqual(self.layer['addressbook'], IAddressBook(42))

import unittest2 as unittest


class MockEntitiesAndOrder(object):
    """Mock wich implements parts of IEntities and IEntityOrder."""

    def __init__(self):
        import icemac.addressbook.address
        self.order = {
            icemac.addressbook.address.postal_address_entity: 0,
            icemac.addressbook.address.phone_number_entity: 10,
            icemac.addressbook.address.e_mail_address_entity: 20,
            icemac.addressbook.address.home_page_address_entity: 30,
            }

    def get(self, entity):
        return self.order[entity]

    def getEntities(self, **kw):
        return self.order.keys()


class PersonDefaultsEntityTest(unittest.TestCase):

    def setUp(self):
        import icemac.addressbook.interfaces
        import zope.component.testing

        zope.component.testing.setUp()
        mock = MockEntitiesAndOrder()
        zope.component.provideUtility(
            mock, icemac.addressbook.interfaces.IEntityOrder)
        zope.component.provideUtility(
            mock, icemac.addressbook.interfaces.IEntities)

    def tearDown(self):
        import zope.component.testing
        zope.component.testing.tearDown()

    def change_sortorder(self):
        import icemac.addressbook.address
        import icemac.addressbook.interfaces
        import zope.component

        # Switching first two entries:
        entity_order = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntityOrder)
        entity_order.order[
            icemac.addressbook.address.postal_address_entity] = 15

    def callFUT(self, sorted=True):
        import icemac.addressbook.person
        pde = icemac.addressbook.person.PersonDefaultsEntity(
            None, icemac.addressbook.interfaces.IPersonDefaults, None)
        return [x[0] for x in pde.getRawFields(sorted=sorted)]

    def test_default_sortorder(self):
        self.assertEqual(
            ['default_postal_address', 'default_phone_number',
             'default_email_address', 'default_home_page_address'],
            self.callFUT())

    def test_changed_sortorder(self):
        self.change_sortorder()
        self.assertEqual(
            ['default_phone_number', 'default_postal_address',
             'default_email_address', 'default_home_page_address'],
            self.callFUT())

    def test_changed_sortorder_not_sorted(self):
        self.change_sortorder()
        self.assertEqual(
            ['default_postal_address', 'default_phone_number',
             'default_email_address', 'default_home_page_address'],
            self.callFUT(sorted=False))


class Person_get_name_Tests(unittest.TestCase):
    """Testing ..person.Person.get_name()."""

    def callMUT(self, first_name=None, last_name=None):
        import icemac.addressbook.person
        person = icemac.addressbook.person.Person()
        if first_name:
            person.first_name = first_name
        if last_name:
            person.last_name = last_name
        return person.get_name()

    def test_returns_last_name_and_first_name_when_existing(self):
        self.assertEqual(u'Bernd Tester', self.callMUT(u'Bernd', u'Tester'))

    def test_returns_last_name_when_first_name_not_existing(self):
        self.assertEqual(u'Tester', self.callMUT(last_name=u'Tester'))

    def test_returns_first_name_when_last_name_not_existing(self):
        self.assertEqual(u'Berns', self.callMUT(first_name=u'Berns'))

    def test_returns_empty_string_when_no_name_exists(self):
        self.assertEqual(u'', self.callMUT())

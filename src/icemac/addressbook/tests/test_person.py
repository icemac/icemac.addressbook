import unittest


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

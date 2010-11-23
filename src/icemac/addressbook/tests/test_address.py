import unittest


class Test_default_attrib_name_to_entity(unittest.TestCase):

    def setUp(self):
        from icemac.addressbook.tests.stubs import setUpStubEntities
        import icemac.addressbook.entities
        import zope.component.testing

        zope.component.testing.setUp()
        setUpStubEntities(self, icemac.addressbook.entities.Entities)

    def tearDown(self):
        import zope.component.testing
        zope.component.testing.tearDown()

    def callFUT(self, name):
        from icemac.addressbook.address import default_attrib_name_to_entity
        return default_attrib_name_to_entity(name)

    def test_unknown_name(self):
        self.assertRaises(ValueError, self.callFUT, 'foo')

    def test_known_name(self):
        self.assertEqual(self.duck, self.callFUT('default_duck'))

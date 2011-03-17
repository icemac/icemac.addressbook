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

    def test_unknown_name_raises_ValueError(self):
        self.assertRaises(ValueError, self.callFUT, 'foo')

    def test_known_name_returns_entity(self):
        self.assertEqual(self.duck, self.callFUT('default_duck'))


class Test_normalize_phone_number(unittest.TestCase):

    def callFUT(self, number, country_code="+49"):
        import icemac.addressbook.address
        return icemac.addressbook.address.normalize_phone_number(
            number, country_code)

    def test_normalized_number_is_returned_unchanged(self):
        self.assertEqual('+491234567890', self.callFUT('+491234567890'))

    def test_everything_but_numbers_and_leading_plus_is_removed(self):
        self.assertEqual('+491234567890', self.callFUT('+49 (1234) 5678 - 90X'))

    def test_leading_zero_is_replaced_by_country_code(self):
        self.assertEqual('+491234567891', self.callFUT('01234/5678-91'))

    def test_only_first_zero_is_replaced_by_country_code(self):
        self.assertEqual('+491234507090', self.callFUT('01234/5070-90'))

    def test_first_zero_is_not_replaced_when_country_code_is_empty(self):
        self.assertEqual('01234567891',
                         self.callFUT('01234/5678-91', country_code=''))

    def test_leading_double_zeros_are_replaced_by_plus(self):
        self.assertEqual('+421234567891', self.callFUT('0042-1234/5678-91'))

    def test_only_leading_double_zeros_are_replaced_by_plus(self):
        self.assertEqual('+421234007891', self.callFUT('0042-1234/0078-91'))

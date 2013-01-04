from mock import patch
import icemac.addressbook.testing
import unittest2 as unittest


class NamesTests(unittest.TestCase):
    """Testing .Names."""

    layer = icemac.addressbook.testing.TEST_BROWSER_LAYER

    def setUp(self):
        from icemac.addressbook.testing import create_person
        super(NamesTests, self).setUp()
        ab = self.layer['addressbook']
        self.p1 = create_person(ab, ab, u'Vrozzek', first_name=u'Paul')
        self.p2 = create_person(ab, ab, u'Vranzz', first_name=u'Peter')

    def test_returns_comma_separated_list_of_names(self):
        from gocept.testing.mock import Property
        from icemac.addressbook.testing import Browser
        browser = Browser()
        browser.login('visitor')
        persons = (
            'icemac.addressbook.browser.search.result.handler.names.Names.'
            'persons')
        with patch(persons, Property()) as persons:
            persons.return_value = [self.p1, self.p2]
            browser.handleErrors = False
            browser.open('http://localhost/ab/@@person-names.html')
            self.assertIn('Paul Vrozzek, Peter Vranzz', browser.contents)

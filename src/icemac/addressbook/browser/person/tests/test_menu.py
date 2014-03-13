from __future__ import unicode_literals
import icemac.addressbook.testing


class PersonListSelectedCheckerTests(
        icemac.addressbook.testing.BrowserTestCase):
    """Tesing ..menu.PersonListSelectedChecker"""

    xpath = '//ul[@id="main-menu"]/li[1]'

    def setUp(self):
        super(PersonListSelectedCheckerTests, self).setUp()
        self.browser = self.get_browser('visitor')

    def assertSelected(self, expected):
        selected = bool(
            self.browser.etree.xpath(self.xpath)[0].attrib.get('class'))
        self.assertEqual(expected, selected)

    def test_person_tab_is_selected_on_person_list(self):
        self.browser.open('http://localhost/ab/@@person-list.html')
        self.assertEqual(  # make sure we test the correct LI
            'Person list',
            self.browser.etree.xpath('%s/a/span' % self.xpath)[0].text)
        self.assertSelected(True)

    def test_person_tab_is_selected_on_persons_view(self):
        ab = self.layer['addressbook']
        tester = icemac.addressbook.testing.create_person(ab, ab, 'Tester')
        self.browser.open(
            'http://localhost/ab/%s/@@export.html' % tester.__name__)
        self.assertSelected(True)

    def test_person_tab_is_not_selected_on_search(self):
        self.browser.open('http://localhost/ab/search.html')
        self.assertSelected(False)

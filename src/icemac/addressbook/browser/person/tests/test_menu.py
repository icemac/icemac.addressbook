from __future__ import unicode_literals
import icemac.addressbook.browser.testing


class PersonListSelectedCheckerTests(
        icemac.addressbook.browser.testing.SiteMenuTestCase):
    """Tesing ..menu.PersonListSelectedChecker"""

    menu_item_index = 0
    menu_item_title = 'Person list'
    menu_item_URL = 'http://localhost/ab/@@person-list.html'
    login_as = 'editor'

    def test_person_tab_is_selected_on_person_list(self):
        self.browser.open(self.menu_item_URL)
        self.assertIsSelected()

    def test_person_tab_is_selected_on_persons_view(self):
        ab = self.layer['addressbook']
        tester = icemac.addressbook.testing.create_person(ab, ab, 'Tester')
        self.browser.open(
            'http://localhost/ab/%s/@@export.html' % tester.__name__)
        self.assertIsSelected()

    def test_person_tab_is_not_selected_on_search(self):
        self.browser.open('http://localhost/ab/search.html')
        self.assertIsNotSelected()

    def test_person_tab_is_selected_on_person_add(self):
        self.browser.open('http://localhost/ab/@@addPerson.html')
        self.assertIsSelected()

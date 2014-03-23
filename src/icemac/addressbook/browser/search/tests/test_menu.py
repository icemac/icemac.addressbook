from __future__ import unicode_literals
import icemac.addressbook.browser.testing


class SearchSelectedCheckerTests(
        icemac.addressbook.browser.testing.SiteMenuTestCase):
    """Tesing ..menu.SearchSelectedChecker"""

    menu_item_index = 1
    menu_item_title = 'Search'
    menu_item_URL = 'http://localhost/ab/@@search.html'
    login_as = 'mgr'

    def test_search_tab_is_selected_on_search_overview(self):
        self.browser.open(self.menu_item_URL)
        self.assertIsSelected()

    def test_search_tab_is_not_selected_on_person_list(self):
        self.browser.open('http://localhost/ab/@@person-list.html')
        self.assertIsNotSelected()

    def test_search_tab_is_selected_on_search_view(self):
        self.browser.open('http://localhost/ab/@@multi_keyword.html')
        self.assertIsSelected()

    def test_search_tab_is_selected_on_search_result_handler_view(self):
        browser = self.browser
        browser.open('http://localhost/ab/@@multi-update')
        self.assertIsSelected()

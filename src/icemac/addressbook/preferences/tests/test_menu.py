from __future__ import unicode_literals
import icemac.addressbook.browser.testing


class PreferencesSelectedCheckerTests(
        icemac.addressbook.browser.testing.SiteMenuTestCase):
    """Testing ..menu.PreferencesSelectedChecker"""

    menu_item_index = 2
    menu_item_title = 'Preferences'
    menu_item_URL = 'http://localhost/ab/++preferences++/ab'
    login_as = 'visitor'

    def test_preferences_tab_is_selected_on_preferences_overview(self):
        self.browser.open(self.menu_item_URL)
        self.assertIsSelected()

    def test_preferences_tab_is_not_selected_on_person_list(self):
        self.browser.open('http://localhost/ab/@@person-list.html')
        self.assertIsNotSelected()

    def test_preferences_tab_is_selected_on_sub_preferences_view(self):
        self.browser.open('http://localhost/ab/++preferences++/ab.timeZone')
        self.assertIsSelected()

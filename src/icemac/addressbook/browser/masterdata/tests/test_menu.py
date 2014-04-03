# Copyright (c) 2014 Michael Howitz
# See also LICENSE.txt
from __future__ import unicode_literals
import icemac.addressbook.browser.testing


class MasterDataSelectedCheckerTests(
        icemac.addressbook.browser.testing.SiteMenuTestCase):
    """Testing ..menu.MasterDataSelectedChecker"""

    menu_item_index = 3
    menu_item_title = 'Master data'
    menu_item_URL = 'http://localhost/ab/@@masterdata.html'
    login_as = 'mgr'

    def test_master_data_tab_is_selected_on_master_data_overview(self):
        self.browser.open(self.menu_item_URL)
        self.assertIsSelected()

    def test_master_data_tab_is_not_selected_on_person_list(self):
        self.browser.open('http://localhost/ab/@@person-list.html')
        self.assertIsNotSelected()

    def test_master_data_tab_is_selected_on_address_book_edit(self):
        self.browser.open('http://localhost/ab/@@edit-address_book.html')
        self.assertIsSelected()

    def test_master_data_tab_is_selected_on_keywords_add(self):
        self.browser.open(
            'http://localhost/ab/++attribute++keywords/@@addKeyword.html')
        self.assertIsSelected()

    def test_master_data_tab_is_selected_on_principals_list(self):
        self.browser.open('http://localhost/ab/++attribute++principals')
        self.assertIsSelected()

    def test_master_data_tab_is_selected_on_user_field_add(self):
        self.browser.open(
            'http://localhost/ab/++attribute++entities/'
            'icemac.addressbook.person.Person/@@addField.html')
        self.assertIsSelected()

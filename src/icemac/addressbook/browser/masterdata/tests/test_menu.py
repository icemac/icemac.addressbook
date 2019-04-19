from __future__ import unicode_literals
import pytest


@pytest.fixture(scope='function')
def md_menu(address_book, browser, sitemenu):
    """Fixture to test the master data menu."""
    browser.login('mgr')
    return sitemenu(
        browser, 4, 'Master data', browser.MASTER_DATA_URL)


def test_menu__master_data_menu__1(md_menu):
    """Asserting that the menu with the index 3 is `Master Data`."""
    assert md_menu.menu_item_title == md_menu.get_menu_item_title_under_test()


def test_menu__master_data_menu__2(md_menu):
    """The master data menu item is selected on the master data overview."""
    assert md_menu.item_selected(md_menu.menu_item_URL)


def test_menu__master_data_menu__3(md_menu):
    """The master data menu item is not selected on the person list."""
    assert not md_menu.item_selected(md_menu.browser.PERSONS_LIST_URL)


def test_menu__master_data_menu__4(md_menu):
    """The master data menu item is selected on address book edit."""
    assert md_menu.item_selected(md_menu.browser.ADDRESS_BOOK_EDIT_URL)


def test_menu__master_data_menu__5(md_menu):
    """The master data menu item is selected on the keywords add form."""
    assert md_menu.item_selected(md_menu.browser.KEYWORD_ADD_URL)


def test_menu__master_data_menu__6(md_menu):
    """The master data menu item is selected on the principals list."""
    assert md_menu.item_selected(md_menu.browser.PRINCIPALS_LIST_URL)


def test_menu__master_data_menu__7(md_menu):
    """The master data menu item is selected on user field add form."""
    assert md_menu.item_selected(md_menu.browser.ENTITY_PERSON_ADD_FIELD_URL)

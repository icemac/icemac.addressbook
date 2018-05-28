from __future__ import unicode_literals
import pytest


@pytest.fixture(scope='function')
def search_menu(address_book, browser, sitemenu):
    """Fixture to test the search menu."""
    browser.login('mgr')  # needed for `test__menu_search_menu__5`.
    return sitemenu(browser, 1, 'Search', browser.SEARCH_URL)


def test__menu_search_menu__1(search_menu):
    """Asserting that the menu with the index 1 is `Search`."""
    assert (search_menu.menu_item_title
            == search_menu.get_menu_item_title_under_test())


def test__menu_search_menu__2(search_menu):
    """The search menu item is selected on the search overview."""
    assert search_menu.item_selected(search_menu.menu_item_URL)


def test__menu_search_menu__3(search_menu):
    """The search menu is not selected on the person list."""
    assert not search_menu.item_selected(search_menu.browser.PERSONS_LIST_URL)


def test__menu_search_menu__4(search_menu):
    """The search menu is selected on the search view."""
    assert search_menu.item_selected(
        'http://localhost/ab/@@multi_keyword.html')


def test__menu_search_menu__5(search_menu):
    """The search menu is selected on the search result handler view."""
    assert search_menu.item_selected('http://localhost/ab/@@multi-update')

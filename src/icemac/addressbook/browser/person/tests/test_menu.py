from __future__ import unicode_literals
import pytest


@pytest.fixture(scope='function')
def pl_menu(address_book, browser, sitemenu):
    """Fixture to test the master data menu."""
    browser.login('editor')
    return sitemenu(
        browser, 0, 'Person list', browser.PERSONS_LIST_URL)


def test_menu__person_list_menu__1(pl_menu):
    """Asserting that the menu with the index 0 is `Person list`."""
    assert pl_menu.menu_item_title == pl_menu.get_menu_item_title_under_test()


def test_menu__person_list_menu__2(pl_menu):
    """The person list menu item is selected on the person list."""
    assert pl_menu.item_selected(pl_menu.menu_item_URL)


def test_menu__person_list_menu__3(address_book, pl_menu, PersonFactory):
    """The person list menu item is selected on the person export view."""
    PersonFactory(address_book, 'Tester')
    assert pl_menu.item_selected(pl_menu.browser.PERSON_EXPORT_URL)


def test_menu__person_list_menu__4(pl_menu):
    """The person list menu item is not selected on the search view."""
    assert not pl_menu.item_selected(pl_menu.browser.SEARCH_URL)


def test_menu__person_list_menu__5(pl_menu):
    """The person list menu item is selected on the person add form."""
    assert pl_menu.item_selected(pl_menu.browser.PERSON_ADD_URL)

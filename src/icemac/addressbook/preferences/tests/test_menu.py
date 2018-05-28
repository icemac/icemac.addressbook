from __future__ import unicode_literals
import pytest


@pytest.fixture(scope='function')
def prefs_menu(address_book, browser, sitemenu):
    """Fixture to test the preferences menu."""
    browser.login('visitor')
    return sitemenu(browser, 2, 'Preferences', browser.PREFS_URL)


def test_menu__preferences_menu__1(prefs_menu):
    """Asserting that the menu with the index 2 is `Preferences`."""
    assert (prefs_menu.menu_item_title
            == prefs_menu.get_menu_item_title_under_test())


def test_menu__preferences_menu__2(prefs_menu):
    """The preferences menu item is selected on the preferences page."""
    assert prefs_menu.item_selected(prefs_menu.menu_item_URL)


def test_menu__preferences_menu__3(prefs_menu):
    """The preferences menu item is not selected on the person list."""
    assert not prefs_menu.item_selected(prefs_menu.browser.PERSONS_LIST_URL)


def test_menu__preferences_menu__4(prefs_menu):
    """The preferences menu item is selected on a sub preferences view."""
    assert prefs_menu.item_selected(prefs_menu.browser.PREFS_TIMEZONE_URL)

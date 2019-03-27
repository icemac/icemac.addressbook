from __future__ import unicode_literals
import pytest


@pytest.fixture(scope='function')
def archive_menu(address_book, browser, sitemenu):
    """Fixture to test the archive menu."""
    browser.login('archivist')
    return sitemenu(browser, 0, 'Archive', browser.ARCHIVE_URL)


def test_menu__archive_menu__1(archive_menu):
    """Asserting that the menu with the index 0 is `Archive`."""
    assert (archive_menu.menu_item_title
            == archive_menu.get_menu_item_title_under_test())


def test_menu__archive_menu__2(archive_menu):
    """The archive tab is selected on the archive overview."""
    assert archive_menu.item_selected(archive_menu.menu_item_URL)


def test_menu__archive_menu__3(archive_menu):
    """The archive tab is not selected on master data."""
    assert not archive_menu.item_selected(archive_menu.browser.MASTER_DATA_URL)


def test_menu__archive_menu__4(address_book, archive_menu, PersonFactory):
    """The archive tab is selected on an archived person."""
    person = PersonFactory(address_book, 'Vrba')
    person.archive()

    assert archive_menu.item_selected(archive_menu.browser.ARCHIVE_PERSON_URL)

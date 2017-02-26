from mock import patch
import pytest


def test_startpage__Dispatch__1(address_book, browser):
    """Dispatch() by default redirects to the welcome page."""
    browser.login('visitor')
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    assert browser.ADDRESS_BOOK_WELCOME_URL == browser.url


@pytest.mark.webdriver
def test_startpage__Dispatch__2(address_book, webdriver):
    """Dispatch() redirects to the page selected on the address book."""
    ab = webdriver.address_book
    webdriver.login('mgr', ab.ADDRESS_BOOK_EDIT_URL)
    ab.startpage = 'Search'
    ab.title = 'Test'
    ab.submit('apply')
    webdriver.open(ab.ADDRESS_BOOK_DEFAULT_URL)
    assert ab.SEARCH_URL == webdriver.path


@pytest.mark.webdriver
def test_startpage__Dispatch__3(address_book, webdriver):
    """If accessing the selected page is not allowed Dispatch() redirects.

    It redirects to the welcome page.

    """
    ab = webdriver.address_book
    webdriver.login('mgr', ab.ADDRESS_BOOK_EDIT_URL)
    ab.startpage = 'Search'
    ab.title = 'Test'
    ab.submit('apply')
    can_access_uri_part = (
        'icemac.addressbook.browser.addressbook.startpage.can_access_uri_part')
    with patch(can_access_uri_part, return_value=False):
        webdriver.open(ab.ADDRESS_BOOK_DEFAULT_URL)
        assert ab.ADDRESS_BOOK_WELCOME_URL == webdriver.path

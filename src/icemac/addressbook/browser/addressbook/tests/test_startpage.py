from mock import patch


def test_startpage__Dispatch__1(address_book, browser):
    """It redirects by default to the welcome page."""
    browser.login('visitor')
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    assert browser.ADDRESS_BOOK_WELCOME_URL == browser.url


def test_startpage__Dispatch__2(address_book, browser):
    """It redirects to the page selected on the address book."""
    browser.login('mgr')
    browser.open(browser.ADDRESS_BOOK_EDIT_URL)
    browser.getControl('start page after log-in').displayValue = 'Search'
    browser.select_favicon()
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    assert browser.SEARCH_URL == browser.url


def test_startpage__Dispatch__3(address_book, browser):
    """If accessing the selected page is not allowed for the user it redirects.

    It redirects to the welcome page.

    """
    browser.login('mgr')
    browser.open(browser.ADDRESS_BOOK_EDIT_URL)
    browser.getControl('start page after log-in').displayValue = 'Search'
    browser.select_favicon()
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message

    can_access_uri_part = (
        'icemac.addressbook.browser.addressbook.startpage.can_access_uri_part')
    with patch(can_access_uri_part, return_value=False):
        browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
        assert browser.ADDRESS_BOOK_WELCOME_URL == browser.url

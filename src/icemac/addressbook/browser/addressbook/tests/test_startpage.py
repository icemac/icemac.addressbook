from mock import patch


def test_startpage__Dispatch__1(address_book, browser):
    """Dispatch() by default redirects to the welcome page."""
    browser.login('visitor')
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    assert browser.ADDRESS_BOOK_WELCOME_URL == browser.url


def test_startpage__Dispatch__2(address_book, webdriver):
    """Dispatch() redirects to the page selected on the address book."""
    sel = webdriver.login('mgr')
    sel.open('/ab/@@edit-address_book.html')
    sel.select('id=form-widgets-startpage', 'label=Search')
    sel.type('id=form-widgets-title', 'Test')
    sel.clickAndWait('id=form-buttons-apply')
    sel.open('/ab')
    assert sel.getLocation().endswith('/ab/@@search.html')


def test_startpage__Dispatch__3(address_book, webdriver):
    """If accessing the selected page is not allowed Dispatch() redirects.

    It redirects to the welcome page.

    """
    sel = webdriver.login('mgr')
    sel.open('/ab/@@edit-address_book.html')
    sel.select('id=form-widgets-startpage', 'label=Search')
    sel.type('id=form-widgets-title', 'Test')
    sel.clickAndWait('id=form-buttons-apply')
    can_access_uri_part = (
        'icemac.addressbook.browser.addressbook.startpage.can_access_uri_part')
    with patch(can_access_uri_part, return_value=False):
        sel.open('/ab')
        assert sel.getLocation().endswith('/ab/@@welcome.html')

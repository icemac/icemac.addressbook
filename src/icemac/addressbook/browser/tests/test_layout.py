from zope.testbrowser.browser import HTTPError
import pytest


def test__layout_pt__1(address_book, browser):
    """layout.pt renders title of the address book in the title tag and h1."""
    address_book.title = u'My addresses'
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    assert 'My addresses' == browser.title
    assert ['My addresses'] == browser.etree.xpath('//h1/span/text()')


def test__layout_pt__2(address_book, browser):
    """layout.pt falls back to the default title if no title is set."""
    address_book.title = u''
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    assert 'icemac.addressbook' == browser.title
    assert ['icemac.addressbook'] == browser.etree.xpath('//h1/span/text()')


def test__layout_pt__3(address_book, browser):
    """layout.pt renders the default title on the root page."""
    browser.login('mgr')  # need to log in to avoid HTTP-401
    browser.open(browser.ROOT_URL)
    assert 'icemac.addressbook' == browser.title
    assert ['icemac.addressbook'] == browser.etree.xpath('//h1/span/text()')


def test__layout_pt__4(address_book, browser):
    """layout.pt renders the default FavIcon on the root page."""
    browser.login('mgr')  # need to log in to avoid HTTP-401
    browser.open(browser.ROOT_URL)
    assert 'href="/++resource++img/favicon-red.ico"' in browser.contents


def test__layout_pt__5(address_book, browser):
    """layout.pt renders the selected FavIcon inside the address book."""
    address_book.favicon = u'/++resource++img/favicon-green.ico'
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    assert 'href="/++resource++img/favicon-green.ico"' in browser.contents


def test__layout_pt__6(address_book, browser):
    """layout.pt renders the NotFound page nicely."""
    with pytest.raises(HTTPError) as err:
        browser.open('http://localhost/I-do-not-exist')
    assert 'HTTP Error 404: Not Found' == str(err.value)
    # If this test fails there was an exception during rendering the error
    # page:
    assert ('The page you are trying to access is not available' in
            browser.contents)


def test__layout_pt__7(address_book, browser):
    """layout.pt renders the Unauthorized page nicely."""
    with pytest.raises(HTTPError) as err:
        browser.open(browser.ROOT_URL)
    assert 'HTTP Error 401: Unauthorized' == str(err.value)
    # If this test fails there was an exception during rendering the error
    # page:
    assert 'You are not authorized.' in browser.contents

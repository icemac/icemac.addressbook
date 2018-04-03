from zope.testbrowser.browser import LinkNotFoundError
import pytest


def test_list__ArchiveList__1(address_book, browser):
    """It is accessible via the site menu."""
    browser.login('archivist')
    browser.open(browser.ADDRESS_BOOK_WELCOME_URL)
    browser.getLink('Archive').click()
    assert browser.url == browser.ARCHIVE_URL


def test_list__ArchiveList__2(address_book, browser):
    """It renders a helpful message if it is empty."""
    browser.login('archivist')
    browser.open(browser.ARCHIVE_URL)
    assert 'There are no persons in the archive yet.' in browser.contents


def test_list__ArchiveList__3(address_book, FullPersonFactory, browser):
    """It renders a list of archived persons."""
    person = FullPersonFactory(
        address_book, u'Vichnaleck', first_name=u'Viktor')
    person.archive()

    browser.login('archivist')
    browser.handleErrors = False
    browser.open(browser.ARCHIVE_URL)
    assert 'Vichnaleck' in browser.contents


@pytest.mark.parametrize('loginname', ['editor', 'visitor'])
def test_list__ArchiveList__4(address_book, browser, loginname):
    """It cannot be accessed by some roles neither via tabs nor URL."""
    browser.login(loginname)
    browser.open(browser.ADDRESS_BOOK_WELCOME_URL)
    with pytest.raises(LinkNotFoundError):
        browser.getLink('Archive').click()
    browser.assert_forbidden(browser.ARCHIVE_URL)

from ..base import BaseSearch
from ..interfaces import ISearch
from zope.interface.verify import verifyObject
import pytest


def test_base__Search__1(address_book, browser):
    """Global navigation provides a link to the search."""
    browser.login('visitor')
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    browser.getLink('Search').click()
    assert browser.SEARCH_URL == browser.url
    # This link leads to the searches overview providing links to the offered
    # search types:
    assert (['Keyword search', 'Name search'] ==
            browser.etree.xpath('//ul[@class="bullet"]/li/a/span/text()'))


def test_base__Search__2(address_book, browser):
    """It cannot be accessed by an archivist."""
    browser.login('archivist')
    browser.assert_forbidden(browser.SEARCH_URL)


def test_base__BaseSearch__1():
    """It implements `ISearch`."""
    assert verifyObject(ISearch, BaseSearch())


def test_base__BaseSearch__search__1():
    """It needs to be implemented by its subclasses."""
    base_search = BaseSearch()
    with pytest.raises(NotImplementedError):
        base_search.search()

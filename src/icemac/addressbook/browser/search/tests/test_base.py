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

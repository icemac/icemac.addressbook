from . import NO_RESULTS_TEXT


def test_name__Search__1(address_book, browser):
    """`Search` for persons who have a name."""
    browser.login('visitor')
    browser.open(browser.SEARCH_URL)
    browser.getLink('Name search').click()
    assert browser.SEARCH_BY_NAME_URL == browser.url
    # An explanation text is displayed:
    assert (
        ['You may use wildcards in this search: Use ? for a single character '
         'or * for multiple characters.'] ==
        browser.etree.xpath(
            '//div[@id="content"]//div[@class="row no-print explanation"]'
            '/text()'))


def test_name__Search__2(address_book, browser):
    """`Search` displays an error message when the search field is empty."""
    browser.login('visitor')
    browser.open(browser.SEARCH_BY_NAME_URL)
    browser.getControl('Search').click()
    assert ['Required input is missing.'] == browser.etree.xpath(
        '//ul[@class="errors"]/li/div/text()')


def test_name__Search__3(address_book, browser):
    """`Search` displays a message when no person is found."""
    browser.login('visitor')
    browser.open(browser.SEARCH_BY_NAME_URL)
    browser.getControl('Name').value = 'Unknown'
    browser.getControl('Search').click()
    assert ('No person found.' == browser.etree.xpath(
        NO_RESULTS_TEXT)[-1].strip())


def test_name__Search__4(search_data, browser):
    """`Search` result is displayed as a table with links to the edit form."""
    browser.login('visitor')
    browser.open(browser.SEARCH_BY_NAME_URL)
    browser.getControl('Name').value = 'Lie*'
    browser.getControl('Search').click()
    assert (['Liebig', 'Tester', 'Liese'] ==  # two search results with 3 links
            browser.etree.xpath('//table/tbody/tr/td/a/text()'))
    assert browser.getLink('Liebig').url.startswith(browser.PERSON_EDIT_URL)
    # The previously entered search string is still there:
    assert 'Lie*' == browser.getControl('Name').value


def test_name__Search__5(search_data, browser):
    """It does not break when searching for `*`.

    But it does not return any results either.
    """
    browser.login('visitor')
    browser.open(browser.SEARCH_BY_NAME_URL)
    browser.getControl('Name').value = '*'
    assert 'No person found.' not in browser.contents
    browser.getControl('Search').click()
    assert 'No person found.' in browser.contents


def test_name__Search__6(address_book, browser):
    """It cannot be accessed by an archivist."""
    browser.login('archivist')
    browser.assert_forbidden(browser.SEARCH_BY_NAME_URL)

from . import NO_RESULTS_TEXT


def test_multi_keyword__Search__1(search_data, browser):
    """`Search` for persons who have specified keywords assigned to."""
    browser.login('visitor')
    browser.open(browser.SEARCH_URL)
    browser.getLink('Keyword search').click()
    assert browser.SEARCH_BY_KEYWORD_URL == browser.url
    # An explanation text is displayed:
    assert (
        ['Select requested keywords from the list popping up when selecting'
         ' the keywords control.'] ==
        browser.etree.xpath(
            '//div[@id="content"]//div[@class="row no-print explanation"]'
            '/text()'))


def test_multi_keyword__Search__2(address_book, browser):
    """When no entry in the keywords field is selected a message is shown."""
    browser.login('visitor')
    browser.open(browser.SEARCH_BY_KEYWORD_URL)
    browser.getControl('Search').click()
    assert ('No person found.' == browser.etree.xpath(
        NO_RESULTS_TEXT)[-1].strip())


def test_multi_keyword__Search__3(search_data, browser):
    """When no result is found a message is shown."""
    browser.login('visitor')
    browser.keyword_search('work')
    assert ('No person found.' == browser.etree.xpath(
        NO_RESULTS_TEXT)[-1].strip())


def test_multi_keyword__Search__4(search_data, browser):
    """`Search` result is displayed as a table with links to the edit form."""
    browser.login('visitor')
    browser.keyword_search('church')
    assert (['Koch', 'Liebig', 'Velleuer'] ==
            browser.etree.xpath('//table/tbody/tr/td/a/text()'))
    assert browser.getLink('Koch').url.startswith(browser.PERSON_EDIT_URL)
    # The previously selected keyword is still selected:
    assert browser.getControl('church').selected


def test_multi_keyword__Search__5(search_data, browser):
    """`Search` uses `and` as default search term concatenation."""
    browser.login('visitor')
    browser.open(browser.SEARCH_BY_KEYWORD_URL)
    assert ['and'] == browser.getControl(
        'search term concatenation').displayValue
    browser.getControl('keywords').displayValue = ['church', 'family']
    browser.getControl('Search').click()
    assert (['Koch', 'Velleuer'] ==
            browser.etree.xpath('//table/tbody/tr/td/a/text()'))


def test_multi_keyword__Search__6(search_data, browser):
    """`Search` can also make an or-search of the selected keywords."""
    browser.login('visitor')
    browser.open(browser.SEARCH_BY_KEYWORD_URL)
    browser.getControl('or').click()
    browser.getControl('keywords').displayValue = ['friends', 'family']
    browser.getControl('Search').click()
    assert (['Hohmuth', 'Koch', 'Velleuer'] ==
            browser.etree.xpath('//table/tbody/tr/td/a/text()'))


def test_multi_keyword__Search__7(address_book, browser):
    """It cannot be accessed by an archivist."""
    browser.login('archivist')
    browser.assert_forbidden(browser.SEARCH_BY_KEYWORD_URL)

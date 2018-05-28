def test_default__add__1i(address_book, browser):
    """The default of the batch size is 20."""
    browser.login('visitor')
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    browser.getLink('Preferences').click()
    assert browser.PREFS_URL == browser.url
    assert '20' == browser.getControl('batch size').value


def test_default__add__2i(address_book, browser):
    """The default sort direction is ascending."""
    browser.login('visitor')
    browser.open(browser.PREFS_URL)
    assert (['ascending (A-->Z)'] ==
            browser.getControl('sort direction').displayValue)


def test_default__add__3i(address_book, browser):
    """The default order by is person's last name."""
    browser.login('visitor')
    browser.open(browser.PREFS_URL)
    assert (['person -- last name'] ==
            browser.getControl('order by').displayValue)


def test_default__add__4i(address_book, browser):
    """By default two columns are displayed in the person lists."""
    browser.login('visitor')
    browser.open(browser.PREFS_URL)
    assert ([
        'person -- last name',
        'person -- first name',
    ] == browser.getControl('columns').displayValue)


def test_default__add__5i(address_book, browser):
    """The default time zone is UTC."""
    browser.login('visitor')
    browser.open(browser.PREFS_TIMEZONE_URL)
    assert ['UTC'] == browser.getControl('Time zone').displayValue

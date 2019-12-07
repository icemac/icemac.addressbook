ADD_MENU_CONTENTS = (
    '/descendant-or-self::ul[@id="add-menu-content"]/li/a/span/text()')


def test_menu__AddMenu__1(address_book, FullPersonFactory, browser):
    """The sort order in the add menu depends on the entity order."""
    FullPersonFactory(address_book, u'Tester')
    browser.login('mgr')
    browser.open(browser.PERSON_EDIT_URL)
    assert ['postal address', 'phone number'] == browser.etree.xpath(
        ADD_MENU_CONTENTS)[:2]

    browser.open(browser.ENTITIES_EDIT_URL)
    browser.getLink('up', index=3).click()
    assert 'Moved phone number up.' == browser.message
    browser.open(browser.PERSON_EDIT_URL)
    assert ['phone number', 'postal address'] == browser.etree.xpath(
        ADD_MENU_CONTENTS)[:2]


def test_menu_MainMenu__1(address_book, browser):
    """It omits deselected tabs from rendering."""
    tab_names_xpath = (
        '//div[@class="menuToggle main-menu"]/ul/li/a/span/text()')
    browser.login('mgr')
    browser.open(browser.ADDRESS_BOOK_EDIT_URL)
    assert [
        'Person list',
        'Search',
        'Archive',
        'Preferences',
        'Master data',
        'About',
    ] == browser.etree.xpath(tab_names_xpath)
    assert [
        'Person list',
        'Search',
        'Archive',
        'Preferences',
        'About',
    ] == browser.getControl('Deselected tabs').displayOptions
    # By default no tabs are deselected:
    assert [] == browser.getControl('Deselected tabs').displayValue

    browser.getControl('Deselected tabs').displayValue = [
        'Search', 'Archive', 'About']
    browser.select_favicon()
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message

    # Deselected tabs are not longer rendered in the UI:
    assert [
        'Person list',
        'Preferences',
        'Master data',
    ] == browser.etree.xpath(tab_names_xpath)
    # This is also true on a sub object:
    browser.getLink('Preferences').click()
    assert [
        'Person list',
        'Preferences',
        'Master data',
    ] == browser.etree.xpath(tab_names_xpath)

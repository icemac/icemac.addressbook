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

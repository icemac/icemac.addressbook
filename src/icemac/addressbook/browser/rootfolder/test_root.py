from zope.testbrowser.browser import HTTPError


def test_root__FrontPage__1(empty_zodb, browser):
    """`FrontPage` shows a message if there is no address book created, yet."""
    browser.login('mgr')
    browser.open(browser.ROOT_URL)
    assert ('There are no address books created yet, click on "Add address '
            'book" to create one' in browser.contents)


def test_root__FrontPage__2(empty_zodb, browser):
    """`FrontPage` cannot be accessed by anonymous."""
    import pytest
    with pytest.raises(HTTPError) as err:
        browser.open(browser.ROOT_URL)
    assert 'HTTP Error 401: Unauthorized' == str(err.value)


def test_root__FrontPage__3(address_book, browser):
    """`FrontPage` lists only address books.

    When another object is in the root folder it is not listed.
    """
    from zope.container.btree import BTreeContainer
    address_book.__parent__['btree'] = BTreeContainer()
    browser.login('mgr')
    browser.open(browser.ROOT_URL)
    assert ['test addressbook'] == browser.etree.xpath('//ul/li/a[1]/text()')


def test_root__FrontPage__4(
        address_book, AddressBookFactory, PersonFactory, browser):
    """`FrontPage` shows number of persons in the address book."""
    ab2 = AddressBookFactory('ab2', u'ab with content')
    ab3 = AddressBookFactory('ab3', u'ab with content, too')
    PersonFactory(ab2, u'Tester')
    PersonFactory(ab3, u'Tester2')
    PersonFactory(ab3, u'Tester3')
    browser.login('mgr')
    browser.open(browser.ROOT_URL)
    assert (['(0 items)', '(1 item)', '(2 items)'] ==
            [x.strip()
             for x in browser.etree.xpath('//ul[@class="bullet"]/li/text()')
             if x.strip()])

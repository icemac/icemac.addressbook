from icemac.addressbook.interfaces import IEntities
from zope.testbrowser.browser import HTTPError
import pytest
import zope.component
import zope.component.hooks


"""The sort order of the entities can be changed globally. The places where
   entities are displayed in order are changed accordingly."""


UP_LINK_URL = ('http://localhost/ab/++attribute++entities/'
               'icemac.addressbook.address.PostalAddress/@@up.html')
DOWN_LINK_URL = ('http://localhost/ab/++attribute++entities/'
                 'icemac.addressbook.addressbook.AddressBook/@@down.html')


def get_entity_titles(address_book):
    """Get the entities of the address book ordered by the sort order."""
    with zope.component.hooks.site(address_book):
        entities = zope.component.getUtility(IEntities)
        return [x.title for x in entities.getEntities()]


def test_entities__1(address_book):
    """There is a default sort order of the entities."""
    assert [u'address book', u'person', u'main adresses and numbers',
            u'postal address'] == get_entity_titles(address_book)[:4]


def test_entities__EntitiesTraverser__publishTraverse__1(
        address_book, browser):
    """It raises a HTTP-404 for unknown entity names."""
    browser.login('mgr')
    with pytest.raises(HTTPError) as err:
        browser.open(browser.ENTITIES_EDIT_URL + '/not.existing.entity')
    assert 'HTTP Error 404: Not Found' == str(err.value)


def test_entities__MoveUp__1(address_book, browser):
    """Selecting the `up` link moves the entity one position up in the list."""
    browser.login('mgr')
    browser.open(browser.ENTITIES_EDIT_URL)
    # Let's move the postal address one up:
    assert UP_LINK_URL == browser.getLink('up', index=2).url
    browser.open(UP_LINK_URL)
    assert 'Moved postal address up.' == browser.message
    assert [u'address book', u'person', u'postal address',
            u'main adresses and numbers'] == get_entity_titles(
                address_book)[:4]


def test_entities__MoveDown__1(address_book, browser):
    """Selecting the `down` link moves the entity one position down in list."""
    browser.login('mgr')
    browser.open(browser.ENTITIES_EDIT_URL)
    # Let's move he address book one down:
    assert DOWN_LINK_URL == browser.getLink('down', index=0).url
    browser.open(DOWN_LINK_URL)
    assert 'Moved address book down.' == browser.message
    assert [u'person', u'address book', u'main adresses and numbers',
            u'postal address'] == get_entity_titles(address_book)[:4]


def test_entities__List__1(address_book, browser):
    """The entity sort order is reflected in the entity table."""
    browser.login('mgr')
    browser.open(DOWN_LINK_URL)
    assert ['person', 'address book', 'main adresses and numbers',
            'postal address'] == browser.etree.xpath(
                '//tbody/tr/td[1]/text()')[:4]  # xpath is one-based!


def test_entities__UpLinkColumn__1(address_book, browser):
    """There is no `up` link for the first entity in the table."""
    browser.login('mgr')
    browser.open(browser.ENTITIES_EDIT_URL)
    assert ['down', 'Edit fields'] == browser.etree.xpath(
        '//tbody/tr[1]/td/a/text()')  # xpath is one-based!


def test_entities__DownLinkColumn__1(address_book, browser):
    """There is no `down` link for the last entity in the table."""
    browser.login('mgr')
    browser.open(browser.ENTITIES_EDIT_URL)
    assert ['up', 'Edit fields'] == browser.etree.xpath(
        '//tbody/tr[last()]/td/a/text()')


@pytest.mark.parametrize('username', ('editor', 'visitor', 'archivist'))
def test_entities__security__1(address_book, browser, username):
    """Non-admin users are not able to change the entity sort order."""
    browser.login(username)
    browser.assert_forbidden(UP_LINK_URL)
    browser.assert_forbidden(DOWN_LINK_URL)

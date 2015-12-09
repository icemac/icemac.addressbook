# -*- coding: utf-8 -*-
from icemac.addressbook.testing import (
    create_person, create_full_person, create_keyword)
import plone.testing
import datetime
import icemac.addressbook.testing


class _SearchLayer(icemac.addressbook.testing._AbstractDataLayer):
    """Layer wich creates base data for searches."""
    defaultBases = (icemac.addressbook.testing.ZODB_LAYER,)

    def createData(self, addressbook):
        friends = self['kw_friends'] = create_keyword(addressbook, u'friends')
        family = self['kw_family'] = create_keyword(addressbook, u'family')
        church = self['kw_church'] = create_keyword(addressbook, u'church')
        self['kw_work'] = create_keyword(addressbook, u'work')
        self['kw_anyone_else'] = create_keyword(addressbook, u'anyone else')
        # person objects are not stored at layer as ZODBIsolatedTestLayer
        # puts a DemoStorage on the storage the persons are created in, so
        # changes on the persons are not visible on the persons stored at
        # the layer.
        create_person(
            addressbook, addressbook, u'Hohmuth', keywords=set([friends]))
        create_full_person(
            addressbook, addressbook, u'Koch', keywords=set([family, church]),
            birth_date=datetime.date(1952, 1, 24), notes=u'father-in-law')
        create_full_person(addressbook, addressbook, u'Velleuer',
                           keywords=set([family, church]))
        create_person(addressbook, addressbook, u'Liebig',
                      keywords=set([church]), notes=u'family')
        create_person(addressbook, addressbook, u'Tester', first_name=u'Liese',
                      birth_date=datetime.date(1976, 11, 15))

    def removeData(self):
        del self['kw_family']
        del self['kw_church']
        del self['kw_work']
        del self['kw_anyone_else']

_SEARCH_LAYER = _SearchLayer(name='SearchLayer')
WSGI_SEARCH_LAYER = icemac.addressbook.testing.TestBrowserLayer(
    'WSGISearch', _SEARCH_LAYER)
SELENIUM_SEARCH_LAYER = plone.testing.Layer(
    name='SeleniumSearch', bases=[_SEARCH_LAYER])


# XXX DEPRECATED
def search_for_persons_with_keyword_search_using_browser(
        layer, keyword, login='mgr'):
    """Searches for all persons with the given keyword.

    Returns the browser.

    """
    browser = icemac.addressbook.testing.get_browser(layer, login)
    browser.open('http://localhost/ab/@@multi_keyword.html')
    browser.getControl('keywords').displayValue = [keyword]
    browser.getControl('Search').click()
    return browser


class SiteMenuTestMixIn(object):
    """Mix-in to test selections in the site menu.

    Expects to be used together with a BrowserTestCase.

    """
    # zero-based index of the position of the item in the menu
    menu_item_index = NotImplemented
    # Title of the menu item, used to make sure the right item is tested.
    menu_item_title = NotImplemented
    # URL to check if the right menu item is tested.
    menu_item_URL = NotImplemented
    login_as = 'visitor'

    def setUp(self):
        super(SiteMenuTestMixIn, self).setUp()
        self.browser = self.get_browser(self.login_as)

    @property
    def _xpath(self):
        # xpath is one based!
        return '//ul[@id="main-menu"]/li[%s]' % (self.menu_item_index + 1)

    def _is_item_selected(self):
        return self.browser.etree.xpath(self._xpath)[0].attrib.get('class')

    def assertIsSelected(self):
        self.assertTrue(self._is_item_selected())

    def assertIsNotSelected(self):
        self.assertFalse(self._is_item_selected())

    def test_assert_correct_menu_item_is_tested(self):
        self.browser.open(self.menu_item_URL)
        self.assertEqual(
            self.menu_item_title,
            self.browser.etree.xpath('%s/a/span' % self._xpath)[0].text)


class SiteMenuTestCase(
        SiteMenuTestMixIn,
        icemac.addressbook.testing.BrowserTestCase):
    """Test case to test selections in the site menu."""

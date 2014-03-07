# -*- coding: utf-8 -*-
# Copyright (c) 2011-2014 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.testing import (
    create_person, create_full_person, create_keyword)
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
SELENIUM_SEARCH_LAYER = icemac.addressbook.testing.SeleniumLayer(
    'SeleniumSearch', _SEARCH_LAYER)


def search_for_persons_with_keyword_search_using_browser(keyword, login='mgr'):
    """Searches for all persons with the given keyword.

    Returns the browser.

    """
    browser = icemac.addressbook.testing.Browser()
    browser.login(login)
    browser.open('http://localhost/ab/@@multi_keyword.html')
    browser.getControl('keywords').displayValue = [keyword]
    browser.getControl('Search').click()
    return browser

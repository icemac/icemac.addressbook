# -*- coding: utf-8 -*-
# Copyright (c) 2011 Michael Howitz
# See also LICENSE.txt

import datetime
import icemac.addressbook.testing
import plone.testing
from icemac.addressbook.testing import (
    create_addressbook, create_person, create_keyword, create_user)
import icemac.addressbook.testing
import transaction

class _SearchLayer(plone.testing.Layer):
    """Layer to test searches."""
    defaultBases = (icemac.addressbook.testing.WSGI_LAYER,)

    def setUp(self):
        icemac.addressbook.testing.setUpStackedDemoStorage(self, 'SearchLayer')
        addressbook = self['addressbook'] = (
            icemac.addressbook.testing.setUpAddressBook(self))
        self['setupZODBConn'], rootObj, rootFolder = (
            icemac.addressbook.testing.createZODBConnection(self['zodbDB']))

        friends = self['kw_friends'] = create_keyword(addressbook, u'friends')
        family = self['kw_family'] = create_keyword(addressbook, u'family')
        church = self['kw_church'] = create_keyword(addressbook, u'church')
        self['kw_work'] = create_keyword(addressbook, u'work')
        self['kw_anyone_else'] = create_keyword(addressbook, u'anyone else')
        self['p_hohmuth'] = create_person(addressbook, addressbook, u'Hohmuth',
                                          keywords=set([friends]))
        self['p_koch'] = create_person(
            addressbook, addressbook, u'Koch', keywords=set([family, church]),
            birth_date=datetime.date(1952, 1, 24))
        self['p_velleuer'] = create_person(
            addressbook, addressbook, u'Velleuer',
            keywords=set([family, church]))
        self['p_liebig'] = create_person(addressbook, addressbook, u'Liebig',
                                         keywords=set([church]))
        transaction.commit()

    def tearDown(self):
        del self['kw_friends']
        del self['kw_family']
        del self['kw_church']
        del self['kw_work']
        del self['kw_anyone_else']
        del self['p_hohmuth']
        del self['p_koch']
        del self['p_velleuer']
        del self['p_liebig']
        del self['addressbook']
        self['setupZODBConn'].close()
        del self['setupZODBConn']
        icemac.addressbook.testing.tearDownStackedDemoStorage(self)

SEARCH_LAYER = _SearchLayer(name='SearchLayer')


class _WSGISearchLayer(icemac.addressbook.testing._WSGITestBrowserLayer):
    defaultBases = (SEARCH_LAYER,)

WSGI_SEARCH_LAYER = _WSGISearchLayer(name='WSGISearchLayer')

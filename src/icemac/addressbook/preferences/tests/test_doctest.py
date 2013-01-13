# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.testing


def test_suite():
    return icemac.addressbook.testing.TestBrowserDocFileSuite(
        'person-list-batching.txt',
        'person-list-userfields.txt',
        'person-list.txt',
        'preferences.txt',
        'sortorder.txt',
        package="icemac.addressbook.preferences")

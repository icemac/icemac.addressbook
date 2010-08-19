# -*- coding: utf-8 -*-
# Copyright (c) 2010 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.testing


def test_suite():
    return icemac.addressbook.testing.FunctionalDocFileSuite(
        'person-list-userfields.txt',
        'person-list.txt',
        'person-list-batching.txt',
        'preferences.txt',
        package="icemac.addressbook.preferences")

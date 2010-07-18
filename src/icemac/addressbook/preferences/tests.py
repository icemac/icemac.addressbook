# -*- coding: utf-8 -*-
# Copyright (c) 2010 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.testing
import icemac.addressbook.preferences

def test_suite():
    return icemac.addressbook.testing.FunctionalDocFileSuite(
        'preferences.txt',
        'person-list.txt',
        package="icemac.addressbook.preferences")

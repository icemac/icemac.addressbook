# -*- coding: latin-1 -*-
# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id$

import icemac.addressbook.export.base
import icemac.addressbook.export.interfaces
import icemac.addressbook.export.xls.simple
import icemac.addressbook.testing
import unittest
import zope.interface.verify

def test_suite():
    return icemac.addressbook.testing.FunctionalDocFileSuite(
        'export.txt',
        'sortorder.txt',
        'userfields.txt',
        package='icemac.addressbook.export',
        )

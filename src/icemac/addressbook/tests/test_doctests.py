# -*- coding: latin-1 -*-
# Copyright (c) 2008-2014 Michael Howitz
# See also LICENSE.txt
# $Id$

import icemac.addressbook.testing
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(icemac.addressbook.testing.FunctionalDocFileSuite(
        # Caution: none of these tests can run as unittest!
        'adapter.txt',
        'address.txt',
        'person.txt',
        ))
    return suite

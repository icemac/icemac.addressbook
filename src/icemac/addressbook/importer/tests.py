# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt

import gocept.reference.verify
import icemac.addressbook.testing
import unittest
import zope.interface.verify
import icemac.addressbook.importer.interfaces
import icemac.addressbook.importer.importer


class TestInterfaces(unittest.TestCase):

    def test_container(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.importer.interfaces.IImporter,
            icemac.addressbook.importer.importer.Importer())


def test_suite():
    return icemac.addressbook.testing.UnittestSuite(TestInterfaces)


# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

import unittest
import zope.interface.verify

import icemac.addressbook.export.interfaces
import icemac.addressbook.export.xls.simple
import icemac.addressbook.testing


class TestInterfaces(unittest.TestCase):

    def test_xls(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.export.interfaces.IExporter,
            icemac.addressbook.export.xls.simple.XLSExport())
        zope.interface.verify.verifyObject(
            icemac.addressbook.export.interfaces.IExporter,
            icemac.addressbook.export.xls.simple.DefaultsExport())
        zope.interface.verify.verifyObject(
            icemac.addressbook.export.interfaces.IExporter,
            icemac.addressbook.export.xls.simple.CompleteExport())


def test_suite():
    suite = icemac.addressbook.testing.UnittestSuite(TestInterfaces)
    suite.addTest(icemac.addressbook.testing.FunctionalDocFileSuite(
            'export/export.txt'))
    return suite


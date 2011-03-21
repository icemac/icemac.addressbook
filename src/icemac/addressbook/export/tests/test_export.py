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


class TestInterfaces(unittest.TestCase):

    def test_BaseExport(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.export.interfaces.IExporter,
            icemac.addressbook.export.base.BaseExporter([], None))

    def test_XLSExport(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.export.interfaces.IExporter,
            icemac.addressbook.export.xls.simple.XLSExport([], None))

    def test_XLSDefaultsExport(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.export.interfaces.IExporter,
            icemac.addressbook.export.xls.simple.DefaultsExport([], None))

    def test_XLSCompleteExport(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.export.interfaces.IExporter,
            icemac.addressbook.export.xls.simple.CompleteExport([], None))


class Test__eq__(unittest.TestCase):

    def setUp(self):
        self.exporter = icemac.addressbook.export.base.BaseExporter(
            [], None)

    def test_not__eq__other_type_number(self):
        self.assertEqual(False, self.exporter == 1)

    def test_not__eq__other_type_object(self):
        self.assertEqual(False, self.exporter == object())

    def test_not__eq__other_class(self):
        other_exporter = icemac.addressbook.export.xls.simple.XLSExport(
            [], None)
        self.assertEqual(False, self.exporter == other_exporter)

    def test___eq__other_instance_same_class(self):
        other_exporter = icemac.addressbook.export.base.BaseExporter(
            [], None)
        self.assertEqual(True, self.exporter == other_exporter)


class Test_export(unittest.TestCase):
    """Test export method of BaseExporter to get better test coverage."""

    def test_export(self):
        exporter = icemac.addressbook.export.base.BaseExporter(None)
        self.assertRaises(NotImplementedError, exporter.export)

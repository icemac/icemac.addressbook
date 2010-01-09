# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.file.file
import icemac.addressbook.file.interfaces
import icemac.addressbook.testing
import os
import os.path
import tempfile
import unittest
import zope.interface.verify


class Base(object):

    fd = None
    filename = None

    def setUp(self):
        self.file = icemac.addressbook.file.file.File()

    def tearDown(self):
        if self.filename and os.path.exists(self.filename):
            os.unlink(self.filename)
        self.filename = None
        if self.fd is not None:
            self.fd.close()
            self.fd = None


class TestFile(Base, unittest.TestCase):
    """Unittests for file."""

    def test_ifile_interface(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.file.interfaces.IFile,
            self.file)

    def test_size_empty_file(self):
        self.assertEqual(0, self.file.size)

    def test_size_file(self):
        self.file.data = '1234567\n90'
        self.assertEqual(10, self.file.size)

    def test_open(self):
        self.fd = self.file.open('w')
        self.fd.write('qwertz.123')
        self.fd.close()
        self.fd = self.file.open('r')
        self.assertEqual('qwertz.123', self.fd.read())

    def test_data_getter(self):
        self.file.data = 'data'
        # the getter of file.data always returns '' to trick z3c.form
        self.assertEqual('', self.file.data)


class FTestFile(Base, icemac.addressbook.testing.FunctionalTestCase):
    """Tests for methods which need functional setup."""

    def test_openDetached(self):
        # need to assign to tree, so commit works
        self.getRootFolder()['f'] = self.file
        self.file.data = 'data\n\nfoobar'
        # commit as openDetached expects a committed blob
        self.commit()
        self.fd = self.file.openDetached()
        self.assertEqual('data\n\nfoobar', self.fd.read())

    def test_replace(self):
        # need to assign to tree, so commit works
        self.getRootFolder()['f2'] = self.file
        self.file.data = '1234'
        fd, self.filename = tempfile.mkstemp()
        os.write(fd, '6789\n0123')
        os.close(fd)
        self.file.replace(self.filename)
        self.commit()
        self.fd = self.file.openDetached()
        self.assertEqual('6789\n0123', self.fd.read())


def test_suite():
    return icemac.addressbook.testing.UnittestSuite(TestFile, FTestFile)


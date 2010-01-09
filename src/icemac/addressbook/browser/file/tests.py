# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

import unittest
from icemac.addressbook.browser.file.file import cleanup_filename
import icemac.addressbook.testing


class Test_cleanup_filename(unittest.TestCase):

    def test_None_filename(self):
        self.assertEqual('<no name>', cleanup_filename(None))

    def test_simple_filename(self):
        self.assertEqual('sample.txt', cleanup_filename('sample.txt'))

    def test_Unix_filename(self):
        self.assertEqual(
            'sample.txt', cleanup_filename('/home/user/sample.txt'))

    def test_Windows_filename(self):
        self.assertEqual(
            'sample.txt', cleanup_filename(r'c:\Users\me\sample.txt'))

    def test_UNC_filename(self):
        self.assertEqual(
            'sample.txt', cleanup_filename(r'\\server\mine\sample.txt'))


def test_suite():
    return icemac.addressbook.testing.UnittestSuite(Test_cleanup_filename)

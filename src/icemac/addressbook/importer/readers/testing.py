# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt

import datetime
import gocept.reference.verify
import icemac.addressbook.importer.interfaces
import icemac.addressbook.testing
import os.path
import unittest
import zope.interface.verify


def getFileHandle(file_name):
    return file(os.path.join(
            os.path.dirname(__file__), 'tests', 'data', file_name))


class BaseReaderTest(unittest.TestCase):
    "Base class for reader tests."

    reader_class = None # set name of reader_class here
    import_file = None # set name of default import file here
    import_file_short = None # set name of short import file here

    def getReader(self, import_file=None):
        if import_file is None:
            import_file = self.import_file
        return self.reader_class.open(getFileHandle(import_file))

    def test_interfaces(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.importer.interfaces.IImportFileReader,
            self.getReader())

    def test_canRead(self):
        self.assertEqual(
            True, self.reader_class.canRead(getFileHandle(self.import_file)))
        self.assertEqual(
            True,
            self.reader_class.canRead(getFileHandle(self.import_file_short)))
        self.assertEqual(
            False, self.reader_class.canRead(getFileHandle('dummy.txt')))

    def test_getFieldNames(self):
        field_names = list(self.getReader().getFieldNames())
        self.assertEqual([u'firstname', u'birth_date', u'last name'],
                         field_names)
        self.assert_(isinstance(field_names[0], unicode))
        self.assert_(isinstance(field_names[1], unicode))
        self.assert_(isinstance(field_names[2], unicode))

    def test_getFieldSamples_firstname(self):
        samples = list(self.getReader().getFieldSamples(u'firstname'))
        self.assertEqual([u'Andreas', u'Hanna', u'Jens'], samples)
        self.assert_(isinstance(samples[0], unicode))
        self.assert_(isinstance(samples[1], unicode))
        self.assert_(isinstance(samples[2], unicode))

    def test_getFieldSamples_lastname(self):
        self.assertEqual([u'Koch', u'Hula', u'Jänsen'],
                         list(self.getReader().getFieldSamples(u'last name')))

    def test_getFieldSamples_birthdate(self):
        samples = list(self.getReader().getFieldSamples(u'birth_date'))
        self.assertEqual([u'1976-01-24', u'2000-01-01', u''], samples)
        self.assert_(isinstance(samples[0], unicode))
        self.assert_(isinstance(samples[1], unicode))
        self.assert_(isinstance(samples[2], unicode))

    def test_getFieldSamples_less_than_3_samples_in_file(self):
        samples = list(self.getReader(self.import_file_short).getFieldSamples(
                u'last name'))
        self.assertEqual([u'Koch'], samples)
        self.assert_(isinstance(samples[0], unicode))

    def test_getFieldSamples_empty_string(self):
        samples = list(self.getReader(self.import_file_short).getFieldSamples(
                u'firstname'))
        self.assertEqual([u''], samples)
        self.assert_(isinstance(samples[0], unicode))


    def test___iter__(self):
        result = [{0: u'Andreas',
                   1: datetime.date(1976, 1, 24),
                   2: u'Koch'},
                  {0: u'Hanna',
                   1: datetime.date(2000, 1, 1),
                   2: u'Hula'},
                  {0: u'Jens',
                   1: None,
                   2: u'Jänsen'},
                  {0: None,
                   1: datetime.date(2001, 12, 31),
                   2: u'Fruma'}]
        for index, line in enumerate(self.getReader()):
            self.assertEqual(result[index], line)
            for key, value in line.items():
                self.assert_(isinstance(key, int), key)
                self.assert_(isinstance(value, unicode) or
                             isinstance(value, datetime.date) or
                             value is None, repr(value))

    def test___iter__short(self):
        result = [{0: None,
                   1: datetime.date(1976, 1, 24),
                   2: u'Koch'}]
        for index, line in enumerate(self.getReader(self.import_file_short)):
            self.assertEqual(result[index], line)
            for key, value in line.items():
                self.assert_(isinstance(key, int), key)
                self.assert_(isinstance(value, unicode) or
                             isinstance(value, datetime.date) or
                             value is None, repr(value))

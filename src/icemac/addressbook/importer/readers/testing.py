# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt

import gocept.reference.verify
import icemac.addressbook.testing
import unittest
import zope.interface.verify
import icemac.addressbook.importer.interfaces
import os.path


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
                u'firstname'))
        self.assertEqual([u'Andreas'], samples)
        self.assert_(isinstance(samples[0], unicode))

    def test___iter__(self):
        result = [{u'birth_date': u'1976-01-24',
                   u'last name': u'Koch',
                   u'firstname': u'Andreas'},
                  {u'birth_date': u'2000-01-01',
                   u'last name': u'Hula',
                   u'firstname': u'Hanna'},
                  {u'birth_date': u'',
                   u'last name': u'Jänsen',
                   u'firstname': u'Jens'},
                  {u'birth_date': u'2001-12-31',
                   u'last name': u'Fruma',
                   u'firstname': u'Fritz'}]
        for index, line in enumerate(self.getReader()):
            self.assertEqual(result[index], line)
            for key, value in line.items():
                self.assert_(isinstance(key, unicode), key)
                self.assert_(isinstance(value, unicode), repr(value))

    def test___iter__short(self):
        result = [{u'birth_date': u'1976-01-24',
                   u'last name': u'Koch',
                   u'firstname': u'Andreas'}]
        for index, line in enumerate(self.getReader(self.import_file_short)):
            self.assertEqual(result[index], line)
            for key, value in line.items():
                self.assert_(isinstance(key, unicode), key)
                self.assert_(isinstance(value, unicode), value)

# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import unittest
import icemac.addressbook.fields
import zope.interface
import zope.schema


class IDummy(zope.interface.Interface):

    dummy = zope.schema.Text(title=u'dummy')
    dummy2 = zope.schema.Text(title=u'dummy2')


class TestFields(unittest.TestCase):

    def setUp(self):
        self.fields = icemac.addressbook.fields.Fields()

    def test_static_fields(self):
        self.assertEqual(
            [('dummy', IDummy['dummy']),
             ('dummy2', IDummy['dummy2'])],
            self.fields.getFieldsInOrder(IDummy))

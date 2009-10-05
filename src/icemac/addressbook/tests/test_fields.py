# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.fields
import icemac.addressbook.interfaces
import unittest
import zope.interface
import zope.interface.exceptions
import zope.schema


class IDummy(zope.interface.Interface):

    dummy = zope.schema.Text(title=u'dummy')
    dummy2 = zope.schema.Text(title=u'dummy2')

class FieldsTests(object):

    fields_class = None

    def setUp(self):
        self.fields = self.fields_class()

    def test_getFieldsInOrder_static_fields(self):
        self.assertEqual(
            [('dummy', IDummy['dummy']),
             ('dummy2', IDummy['dummy2'])],
            self.fields.getFieldsInOrder(IDummy))

    def test_getFieldValuesInOrder(self):
        self.assertEqual(
            [IDummy['dummy'], IDummy['dummy2']],
            self.fields.getFieldValuesInOrder(IDummy))


class TestFields(FieldsTests, unittest.TestCase):

    fields_class = icemac.addressbook.fields.Fields


class TestPersistentFields(FieldsTests, unittest.TestCase):

    fields_class = icemac.addressbook.fields.PersistentFields

class TestField(unittest.TestCase):

    def setUp(self):
        self.field = icemac.addressbook.fields.Field()
        self.field.title = u'my field'
        self.field.order = 1.5

    def test_invariants_no_choice(self):
        # There is no invariant when the type is not `choice`.
        self.field.type = u'Text'
        errors = zope.schema.getValidationErrors(
            icemac.addressbook.interfaces.IField, self.field)
        self.assertEqual([], errors)

    def test_invariants_choice_no_values(self):
        # Using `choice` type requires values
        self.field.type = u'Choice'
        errors = zope.schema.getValidationErrors(
            icemac.addressbook.interfaces.IField, self.field)
        self.assertEqual(1, len(errors))
        self.assert_(errors[0][0] is None)
        self.assert_(
            isinstance(errors[0][1], zope.interface.exceptions.Invalid))
        self.assertEqual(errors[0][1].args,
                         (u'type "choice" requires values.',))

    def test_invariants_choice_with_values(self):
        self.field.type = u'Choice'
        self.field.values = [u'sure', u'not really']
        errors = zope.schema.getValidationErrors(
            icemac.addressbook.interfaces.IField, self.field)
        self.assertEqual([], errors)

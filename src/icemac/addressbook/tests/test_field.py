# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.entities
import icemac.addressbook.interfaces
import unittest
import zope.interface
import zope.interface.exceptions
import zope.schema


class TestField(unittest.TestCase):

    def setUp(self):
        self.field = icemac.addressbook.entities.Field()
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
        self.assertEqual(
            (u'type "choice" requires at least one field value.',),
            errors[0][1].args)

    def test_invariants_choice_with_values(self):
        self.field.type = u'Choice'
        self.field.values = [u'sure', u'not really']
        errors = zope.schema.getValidationErrors(
            icemac.addressbook.interfaces.IField, self.field)
        self.assertEqual([], errors)

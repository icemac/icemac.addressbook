# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Michael Howitz
# See also LICENSE.txt
from __future__ import absolute_import
import mock
import unittest2 as unittest


class Test_update_persons(unittest.TestCase):
    """Testing .base.update_persons."""

    def setUp(self):
        import grokcore.component.testing
        import zope.annotation.attribute
        import zope.component
        import zope.component.testing
        base = 'icemac.addressbook.browser.search.result.handler.update'
        grokcore.component.testing.grok(base + '.operators')
        grokcore.component.testing.grok(base + '.errormessages')
        zope.component.provideAdapter(
            zope.annotation.attribute.AttributeAnnotations)
        self.addCleanup(zope.component.testing.tearDown)

    def test_updates_only_specified_field(self):
        from icemac.addressbook.person import Person, person_entity
        from ..base import update_persons
        person1 = Person()
        person1.notes = u'p1'
        person2 = Person()
        person2.notes = u'p2'
        update_persons((person1, person2), person_entity,
                       person_entity.getRawField('notes'), 'append', u'bar')
        self.assertEqual('p1bar', person1.notes)
        self.assertEqual('p2bar', person2.notes)
        # no other attributes are in vars as they are not changed (only the
        # private container attributes are additionally here).
        self.assertEqual(
            ['notes', '_BTreeContainer__len', '_SampleContainer__data'],
            vars(person1).keys())

    @mock.patch('icemac.addressbook.browser.search.result.handler.update.'
                'operators.NoneAppend.__call__')
    def test_returns_custom_ZeroDivisionError_if_division_by_zero_occurred(
            self, op):
        from icemac.addressbook.person import Person, person_entity
        from ..base import update_persons
        op.side_effect = ZeroDivisionError
        person1 = Person()
        person1.__name__ = 'person1'
        result = update_persons(
            [person1], person_entity,
            person_entity.getRawField('notes'), 'append', u'bar')
        self.assertEqual({'person1': u'Division by zero'}, result)

    @mock.patch('icemac.addressbook.browser.search.result.handler.update.'
                'operators.NoneAppend.__call__')
    def test_returns_custom_Exception_if_other_exception_occurred(self, op):
        from ..base import update_persons
        from icemac.addressbook.person import Person, person_entity
        import zope.i18n
        op.side_effect = IOError('file not found')
        person1 = Person()
        person1.__name__ = 'person1'
        result = update_persons(
            [person1], person_entity,
            person_entity.getRawField('notes'), 'append', u'bar')
        self.assertEqual(
            [('person1',
              u'Unexpected error occurred: IOError: file not found')],
            [(key, zope.i18n.translate(val)) for key, val in result.items()])

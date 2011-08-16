from __future__ import absolute_import
import unittest2 as unittest


class Test_update_persons(unittest.TestCase):
    """Testing .base.update_persons."""

    def setUp(self):
        import grokcore.component.testing
        import zope.component.testing
        grokcore.component.testing.grok(
            'icemac.addressbook.browser.search.result.handler.update.operators'
            )
        self.addCleanup(zope.component.testing.tearDown)


    def test_update_persons_updates_only_specified_field(self):
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

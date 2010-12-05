# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.orderstorage
import unittest


class BaseTestOrderStorage(unittest.TestCase):

    def setUp(self):
        self.storage = icemac.addressbook.orderstorage.OrderStorage()


class TestOrderStorage(BaseTestOrderStorage):

    def test_add(self):
        self.assertEqual([], list(self.storage.namespaces()))

        self.storage.add('foo', 'bar')
        self.assertEqual(['bar'], list(self.storage.namespaces()))
        self.assertEqual(['foo'], list(self.storage.__iter__('bar')))

        self.storage.add('foo2', 'bar2')
        self.assertEqual(['bar', 'bar2'], sorted(self.storage.namespaces()))
        self.assertEqual(['foo'], list(self.storage.__iter__('bar')))
        self.assertEqual(['foo2'], list(self.storage.__iter__('bar2')))

        self.storage.add('foo2', 'bar')
        self.assertEqual(['bar', 'bar2'], sorted(self.storage.namespaces()))
        self.assertEqual(
            ['foo', 'foo2'], list(self.storage.__iter__('bar')))
        self.assertEqual(['foo2'], list(self.storage.__iter__('bar2')))

    def test_add_duplicate_no_error(self):
        self.storage.add('foo', 'bar')
        self.storage.add('foo', 'bar')
        self.assertEqual(['bar'], list(self.storage.namespaces()))
        self.assertEqual(['foo'], list(self.storage.__iter__('bar')))

    def test_add_duplicate_does_not_change_sortorder(self):
        self.storage.add('foo1', 'bar')
        self.storage.add('foo3', 'bar')
        self.storage.add('foo2', 'bar')
        self.storage.add('foo3', 'bar')
        self.assertEqual(
            ['foo1', 'foo3', 'foo2'], list(self.storage.__iter__('bar')))

    def test_add_duplicate_other_namespace(self):
        self.storage.add('foo', 'bar')
        self.storage.add('foo', 'bar2')
        self.assertEqual(
            ['bar', 'bar2'], sorted(self.storage.namespaces()))
        self.assertEqual(['foo'], list(self.storage.__iter__('bar')))
        self.assertEqual(['foo'], list(self.storage.__iter__('bar2')))

    def test_remove(self):
        self.storage.add('foo', 'bar')
        self.storage.add('foo2', 'bar2')
        self.storage.add('foo2', 'bar')

        self.storage.remove('foo', 'bar')
        self.assertEqual(['bar', 'bar2'], sorted(self.storage.namespaces()))
        self.assertEqual(['foo2'], list(self.storage.__iter__('bar')))
        self.assertEqual(['foo2'], list(self.storage.__iter__('bar2')))

        self.storage.remove('foo2', 'bar2')
        self.assertEqual(['bar', 'bar2'], sorted(self.storage.namespaces()))
        self.assertEqual(['foo2'], list(self.storage.__iter__('bar')))
        self.assertEqual([], list(self.storage.__iter__('bar2')))

        self.storage.remove('foo2', 'bar')
        self.assertEqual(['bar', 'bar2'], sorted(self.storage.namespaces()))
        self.assertEqual([], list(self.storage.__iter__('bar')))
        self.assertEqual([], list(self.storage.__iter__('bar2')))

    def test_remove_not_existing_namespace(self):
        self.storage.add('fuz', 'baz')
        self.assertRaises(KeyError, self.storage.remove, 'foo', 'bar')

    def test_remove_not_existing_obj(self):
        self.storage.add('fuz', 'bar')
        self.assertRaises(ValueError, self.storage.remove, 'foo', 'bar')

    def test_get__not_existing_namespace(self):
        self.assertRaises(KeyError, self.storage.get, 'foo1', 'bar')

    def test_get__not_existing_obj(self):
        self.storage.add('foo1', 'bar')
        self.assertRaises(KeyError, self.storage.get, 'foo2', 'bar')

    def test_get__existing_in_other_namespace(self):
        self.storage.add('foo1', 'baz')
        self.assertRaises(KeyError, self.storage.get, 'foo1', 'bar')

    def test_truncate_not_existing_namespace(self):
        self.storage.truncate('baz')
        # Truncation does not create a new namespace when it does not exist:
        self.assertEqual([], sorted(self.storage.namespaces()))

    def test_truncate_existing_namespace(self):
        self.storage.add('foo1', 'bar')
        self.storage.add('foo2', 'bar')
        self.storage.add('foo1', 'baz')
        self.storage.truncate('bar')
        # The specified namespace is empty, others are untouched:
        self.assertEqual([], list(self.storage.__iter__('bar')))
        self.assertEqual(['foo1'], list(self.storage.__iter__('baz')))


class TestOrderStorageMovement(BaseTestOrderStorage):

    def setUp(self):
        super(TestOrderStorageMovement, self).setUp()
        self.storage.add('foo1', 'bar')
        self.storage.add('foo2', 'bar')
        self.storage.add('foo3', 'bar')
        self.storage.add('foo4', 'bar')
        self.storage.add('baz', 'fuz')

    def test_up(self):
        self.assertEqual(['foo1', 'foo2', 'foo3', 'foo4'],
                         list(self.storage.__iter__('bar')))
        self.storage.up('foo3', 'bar')
        self.assertEqual(['foo1', 'foo3', 'foo2', 'foo4'],
                         list(self.storage.__iter__('bar')))
        self.assertEqual(['baz'], list(self.storage.__iter__('fuz')))
        self.assertEqual(1, self.storage.get('foo3', 'bar'))
        self.storage.up('foo3', 'bar')
        self.assertEqual(['foo3', 'foo1', 'foo2', 'foo4'],
                         list(self.storage.__iter__('bar')))
        self.assertEqual(0, self.storage.get('foo3', 'bar'))

    def test_up_first_element(self):
        self.assertRaises(ValueError, self.storage.up, 'foo1', 'bar')

    def test_down(self):
        self.storage.down('foo3', 'bar')
        self.assertEqual(['foo1', 'foo2', 'foo4', 'foo3'],
                         list(self.storage.__iter__('bar')))
        self.assertEqual(['baz'], list(self.storage.__iter__('fuz')))
        self.assertEqual(0, self.storage.get('foo1', 'bar'))
        self.storage.down('foo1', 'bar')
        self.assertEqual(['foo2', 'foo1', 'foo4', 'foo3'],
                         list(self.storage.__iter__('bar')))
        self.assertEqual(1, self.storage.get('foo1', 'bar'))

    def test_down_last_element(self):
        self.assertRaises(ValueError, self.storage.down, 'foo4', 'bar')

    def test_up_delta(self):
        self.storage.up('foo3', 'bar', 2)
        self.assertEqual(['foo3', 'foo1', 'foo2', 'foo4'],
                         list(self.storage.__iter__('bar')))

    def test_up_first_element_delta(self):
        self.assertRaises(ValueError, self.storage.up, 'foo2', 'bar', 2)

    def test_down_delta(self):
        self.storage.down('foo2', 'bar', 2)
        self.assertEqual(['foo1', 'foo3', 'foo4', 'foo2'],
                         list(self.storage.__iter__('bar')))

    def test_down_last_element_delta(self):
        self.assertRaises(ValueError, self.storage.down, 'foo3', 'bar', 2)

    def test_down_delta_0(self):
        self.storage.down('foo2', 'bar', 0)
        self.assertEqual(['foo1', 'foo2', 'foo3', 'foo4'],
                         list(self.storage.__iter__('bar')))

    def test_down_delta_negative(self):
        self.storage.down('foo2', 'bar', -2)
        self.assertEqual(['foo1', 'foo2', 'foo3', 'foo4'],
                         list(self.storage.__iter__('bar')))

    def test_get(self):
        self.storage.add('foo2', 'baz')
        self.assertEqual(1, self.storage.get('foo2', 'bar'))
        self.assertEqual(0, self.storage.get('foo2', 'baz'))

    def test_isFirst_not_in_List(self):
        self.assertRaises(KeyError, self.storage.isFirst, 'foo', 'fuz')

    def test_isFirst_not_first(self):
        self.assert_(self.storage.isFirst('foo2', 'bar') is False)
        self.assert_(self.storage.isFirst('foo3', 'bar') is False)
        self.assert_(self.storage.isFirst('foo4', 'bar') is False)

    def test_isFirst_first(self):
        self.assertTrue(self.storage.isFirst('foo1', 'bar'))
        self.assertTrue(self.storage.isFirst('baz', 'fuz'))

    def test_isLast_not_in_List(self):
        self.assertRaises(KeyError, self.storage.isLast, 'foo', 'fuz')

    def test_isLast_not_last(self):
        self.assert_(self.storage.isLast('foo1', 'bar') is False)
        self.assert_(self.storage.isLast('foo2', 'bar') is False)
        self.assert_(self.storage.isLast('foo3', 'bar') is False)

    def test_isLast_last(self):
        self.assertTrue(self.storage.isLast('foo4', 'bar'))
        self.assertTrue(self.storage.isLast('baz', 'fuz'))

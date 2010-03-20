# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.orderstorage
import unittest


class TestOrderStorage(unittest.TestCase):

    def setUp(self):
        self.storage = icemac.addressbook.orderstorage.OrderStorage()

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

    def test_up(self):
        self.storage.add('foo', 'bar')
        self.storage.add('foo2', 'bar')
        self.storage.add('foo3', 'bar')
        self.storage.add('foo4', 'bar')
        self.storage.add('baz', 'fuz')
        self.assertEqual(['foo', 'foo2', 'foo3', 'foo4'],
                         list(self.storage.__iter__('bar')))
        self.storage.up('foo3', 'bar')
        self.assertEqual(['foo', 'foo3', 'foo2', 'foo4'],
                         list(self.storage.__iter__('bar')))
        self.assertEqual(['baz'], list(self.storage.__iter__('fuz')))
        self.assertEqual(1, self.storage.get('foo3', 'bar'))
        self.storage.up('foo3', 'bar')
        self.assertEqual(['foo3', 'foo', 'foo2', 'foo4'],
                         list(self.storage.__iter__('bar')))
        self.assertEqual(0, self.storage.get('foo3', 'bar'))

    def test_up_first_element(self):
        self.storage.add('foo', 'bar')
        self.assertRaises(ValueError, self.storage.up, 'foo', 'bar')

    def test_down(self):
        self.storage.add('foo', 'bar')
        self.storage.add('foo2', 'bar')
        self.storage.add('foo3', 'bar')
        self.storage.add('foo4', 'bar')
        self.storage.add('baz', 'fuz')
        self.storage.down('foo3', 'bar')
        self.assertEqual(['foo', 'foo2', 'foo4', 'foo3'],
                         list(self.storage.__iter__('bar')))
        self.assertEqual(['baz'], list(self.storage.__iter__('fuz')))
        self.assertEqual(0, self.storage.get('foo', 'bar'))
        self.storage.down('foo', 'bar')
        self.assertEqual(['foo2', 'foo', 'foo4', 'foo3'],
                         list(self.storage.__iter__('bar')))
        self.assertEqual(1, self.storage.get('foo', 'bar'))

    def test_down_last_element(self):
        self.storage.add('foo', 'bar')
        self.assertRaises(ValueError, self.storage.down, 'foo', 'bar')

    def test_get__not_existing(self):
        self.assertRaises(KeyError, self.storage.get, 'foo', 'bar')

    def test_get__existing_in_other_namespace(self):
        self.storage.add('foo', 'baz')
        self.assertRaises(KeyError, self.storage.get, 'foo', 'bar')

    def test_get(self):
        self.storage.add('foo3', 'bar')
        self.storage.add('foo2', 'bar')
        self.storage.add('foo1', 'bar')
        self.storage.add('foo2', 'baz')
        self.assertEqual(1, self.storage.get('foo2', 'bar'))
        self.assertEqual(0, self.storage.get('foo2', 'baz'))


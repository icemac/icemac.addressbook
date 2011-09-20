from __future__ import unicode_literals
from decimal import Decimal
import icemac.addressbook.testing
import unittest


class TestOperators(unittest.TestCase):
    """Testing ..operators.*"""

    layer = icemac.addressbook.testing.ZODB_ISOLATED_TEST_LAYER

    def callOP(self, value1, value2, operator_name):
        import zope.component
        from ..operators import IOperator
        operator = zope.component.getAdapter(
            value1, IOperator, name=operator_name)
        return operator(value2)

    def create_folders(self, quantity):
        """Create some folders needed for keyword tests."""
        from icemac.addressbook.utils import create_and_add
        from zope.container.folder import Folder
        root = self.layer['rootFolder']
        folders = tuple()
        for i in range(quantity):
            folders += (root[create_and_add(root, Folder)], )
        return folders

    def assert_set_op(self, expected, operand1, operator, operand2):
        from gocept.reference.collection import InstrumentedSet
        import zope.component.hooks
        old_site = zope.component.hooks.getSite()
        try:
            zope.component.hooks.setSite(self.layer['rootFolder'])
            self.assertEqual(
                set(expected),
                self.callOP(
                    InstrumentedSet(operand1), set(operand2), operator))
        finally:
            zope.component.hooks.setSite(old_site)

    def test_append_returns_value2_if_value2_is_None(self):
        self.assertEqual('bar', self.callOP(None, u'bar', 'append'))

    def test_append_returns_concatenation_for_unicode(self):
        self.assertEqual('foobar', self.callOP('foo', 'bar', 'append'))

    def test_replace_returns_value2_for_unicodes(self):
        self.assertEqual('bar', self.callOP('foo', 'bar', 'replace'))

    def test_replace_returns_value2_for_ints(self):
        self.assertEqual(2, self.callOP(1, 2, 'replace'))

    def test_prepend_with_None_returns_value2(self):
        self.assertEqual('bar', self.callOP(None, 'bar', 'prepend'))

    def test_prepend_returns_inverse_concatenation_of_append(self):
        self.assertEqual('barfoo', self.callOP('foo', 'bar', 'prepend'))

    def test_remove_all_removes_all_occurrences_of_value2_in_value1(self):
        self.assertEqual('bac', self.callOP('abbaabc', 'ab', 'remove-all'))

    def test_remove_all_does_nothing_on_None(self):
        self.assertEqual(None, self.callOP(None, 'a', 'remove-all'))

    def test_remove_first_removes_only_first_occurrence_of_value2(self):
        self.assertEqual('ddab', self.callOP('abddab', 'ab', 'remove-first'))

    def test_remove_first_does_nothing_on_None(self):
        self.assertEqual(None, self.callOP(None, 'a', 'remove-first'))

    def test_remove_last_removes_only_last_occurrence_of_value2(self):
        self.assertEqual('abdd', self.callOP('abddab', 'ab', 'remove-last'))

    def test_remove_last_does_nothing_on_None(self):
        self.assertEqual(None, self.callOP(None, 'a', 'remove-last'))

    def test_union_returns_union_of_values(self):
        f1, f2, f3 = self.create_folders(3)
        self.assert_set_op([f1, f2, f3], [f1, f2], 'union', [f2, f3])

    def test_difference_returns_difference_of_values(self):
        f1, f2, f3, f4 = self.create_folders(4)
        self.assert_set_op([f1, f3],
                           [f1, f2, f3, f4], 'difference', [f2, f4])

    def test_intersection_returns_intersection_of_values(self):
        f1, f2, f3, f4 = self.create_folders(4)
        self.assert_set_op([f2],
                           [f1, f2, f3], 'intersection', [f2, f4])

    def test_symmetric_difference_returns_symmetric_difference_of_values(self):
        f1, f2, f3 = self.create_folders(3)
        self.assert_set_op([f1, f3],
                           [f1, f2], 'symmetric_difference', [f2, f3])

    def test_add_returns_value2_on_None(self):
        self.assertEqual(2, self.callOP(None, 2, 'add'))

    def test_add_returns_sum_of_value1_and_value2(self):
        self.assertEqual(3, self.callOP(1, 2, 'add'))

    def test_add_returns_sum_of_value1_and_value2_for_decimals(self):
        self.assertEqual(Decimal(3),
                         self.callOP(Decimal(1), Decimal(2), 'add'))

    def test_sub_returns_neg_value2_on_None(self):
        self.assertEqual(-2, self.callOP(None, 2, 'sub'))

    def test_sub_returns_difference_of_value1_and_value2(self):
        self.assertEqual(-1, self.callOP(1, 2, 'sub'))

    def test_sub_returns_difference_of_value1_and_value2_for_decimals(self):
        self.assertEqual(Decimal(-1),
                         self.callOP(Decimal(1), Decimal(2), 'sub'))

    def test_mul_returns_0_on_None(self):
        self.assertEqual(0, self.callOP(None, 2, 'mul'))

    def test_mul_returns_product_of_value1_and_value2(self):
        self.assertEqual(6, self.callOP(3, 2, 'mul'))

    def test_mul_returns_product_of_value1_and_value2_for_decimals(self):
        self.assertEqual(Decimal(6),
                         self.callOP(Decimal(3), Decimal(2), 'mul'))

    def test_div_returns_0_on_None(self):
        self.assertEqual(0, self.callOP(None, 2, 'div'))

    def test_div_returns_whole_number_quotient_of_value1_and_value2(self):
        self.assertEqual(3, self.callOP(10, 3, 'div'))

    def test_div_returns_quotient_of_value1_and_value2(self):
        self.assertEqual(Decimal(10) / Decimal(3),
                         self.callOP(Decimal(10), Decimal(3), 'div'))

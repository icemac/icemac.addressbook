from __future__ import unicode_literals

from ..operators import IOperator, Operator
from decimal import Decimal
from gocept.reference.collection import InstrumentedSet
from icemac.addressbook.utils import create_and_add
from zope.container.folder import Folder
import pytest
import zope.component
import zope.component.hooks


# Fixtures to set-up infrastructure which are usable in tests:

@pytest.fixture(scope='function')
def folders(addressBookConnectionF):
    """Fixture returning a callable to create a number of folders."""
    def create_folders(quantity):
        """Create `quantity` folders needed for keyword tests."""
        root = addressBookConnectionF.rootFolder
        names = []
        for _ in range(quantity):
            names.append(create_and_add(root, Folder))
        return tuple(root[name] for name in names)
    return create_folders


# Fixtures to help asserting

@pytest.fixture(scope='session')
def evaluate(zcmlS):
    """Fixture returning a callable to do an operation."""
    return _evaluate


@pytest.fixture(scope='function')
def set_evaluate(addressBookConnectionF):
    """Fixture returning a callable to do a set operation."""
    def _set_evaluate(value1, operator_name, value2):
        """Compute a set operation."""
        with zope.component.hooks.site(addressBookConnectionF.rootFolder):
            return _evaluate(
                InstrumentedSet(value1), operator_name, set(value2))
    return _set_evaluate


# Helper functions

def _evaluate(value1, operator_name, value2):
    """Compute an operation."""
    operator = zope.component.getAdapter(value1, IOperator, name=operator_name)
    return operator(value2)


# Tests

def test_operator__Operator____call____1():
    """It raises an NotImplementedError."""
    op = Operator(None)
    with pytest.raises(NotImplementedError):
        op(None)


def test_operator__append__1(evaluate):
    """append() returns value2 if value1 is `None`."""
    assert 'bar' == evaluate(None, 'append', 'bar')


def test_operator__append__2(evaluate):
    """append() returns concatenation for unicode."""
    assert 'foobar' == evaluate('foo', 'append', 'bar')


def test_operator__replace__1(evaluate):
    """replace() returns value2 for unicodes."""
    assert 'bar' == evaluate('foo', 'replace', 'bar')


def test_operator__replace__2(evaluate):
    """replace() returns value2 for ints."""
    assert 2 == evaluate(1, 'replace', 2)


def test_operator__prepend__1(evaluate):
    """prepend() with `None` returns value2."""
    assert 'bar' == evaluate(None, 'prepend', 'bar')


def test_operator__prepend__2(evaluate):
    """prepend() returns the inverse concatenation of `append`."""
    assert 'barfoo' == evaluate('foo', 'prepend', 'bar')


def test_operator__remove_all__1(evaluate):
    """remove-all() removes all occurrences of value2 in value1."""
    assert 'bac' == evaluate('abbaabc', 'remove-all', 'ab')


def test_operator__remove_all__2(evaluate):
    """remove-all() does nothing on `None`."""
    assert None is evaluate(None, 'remove-all', 'a')


def test_operator__remove_first__1(evaluate):
    """remove-first() removes only the first occurrence of value2."""
    assert 'ddab' == evaluate('abddab', 'remove-first', 'ab')


def test_operator__remove_first__2(evaluate):
    """remove-first() does nothing on `None`."""
    assert None is evaluate(None, 'remove-first', 'a')


def test_operator__remove_last__1(evaluate):
    """remove-last() removes only the last occurrence of value2."""
    assert 'abdd' == evaluate('abddab', 'remove-last', 'ab')


def test_operator__remove_last__2(evaluate):
    """remove-last() does nothing on `None`."""
    assert None is evaluate(None, 'remove-last', 'a')


def test_operator__union__1(folders, set_evaluate):
    """union() returns the union of the values."""
    f1, f2, f3 = folders(3)
    assert set([f1, f2, f3]) == set_evaluate([f1, f2], 'union', [f2, f3])


def test_operator__difference__1(folders, set_evaluate):
    """difference() returns the difference of the values."""
    f1, f2, f3, f4 = folders(4)
    assert set([f1, f3]) == set_evaluate(
        [f1, f2, f3, f4], 'difference', [f2, f4])


def test_operator__intersection__1(folders, set_evaluate):
    """intersection() returns the intersection of the values."""
    f1, f2, f3, f4 = folders(4)
    assert set([f2]) == set_evaluate([f1, f2, f3], 'intersection', [f2, f4])


def test_operator__symmetric_difference__1(folders, set_evaluate):
    """symmetric-difference() returns symmetric difference of the values."""
    f1, f2, f3 = folders(3)
    assert set([f1, f3]) == set_evaluate(
        [f1, f2], 'symmetric_difference', [f2, f3])


def test_operator__add__1(evaluate):
    """add() returns value2 if value1 is `None`."""
    assert 2 == evaluate(None, 'add', 2)


@pytest.mark.parametrize("datatype", (int, Decimal))
def test_operator__add__2(evaluate, datatype):
    """add() returns the sum of value1 and value2."""
    assert datatype(3) == evaluate(datatype(1), 'add', datatype(2))


def test_operator__sub__1(evaluate):
    """sub() returns the negative value of value2 if value1 is `None`."""
    assert -2 == evaluate(None, 'sub', 2)


@pytest.mark.parametrize("datatype", (int, Decimal))
def test_operator__sub__2(evaluate, datatype):
    """sub() returns the difference of value1 and value2."""
    assert datatype(-1) == evaluate(datatype(1), 'sub', datatype(2))


def test_operator__mul__1(evaluate):
    """mul() returns 0 on if value1 is `None`."""
    assert 0 == evaluate(None, 'mul', 2)


@pytest.mark.parametrize("datatype", (int, Decimal))
def test_operator__mul__2(evaluate, datatype):
    """mul() returns the product of value1 and value2."""
    assert datatype(6) == evaluate(datatype(3), 'mul', datatype(2))


def test_operator__div__1(evaluate):
    """div() returns 0 if value1 is `None`."""
    assert 0 == evaluate(None, 'div', 2)


@pytest.mark.parametrize("datatype", (int, Decimal))
def test_operator__div__2(evaluate, datatype):
    """div() returns the quotient depending on the data type of the values."""
    assert datatype(10) // datatype(3) == evaluate(
        datatype(10), 'div', datatype(3))

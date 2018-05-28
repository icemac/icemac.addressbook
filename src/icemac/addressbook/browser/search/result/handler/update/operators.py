# -*- coding: utf-8 -*-
import decimal
import gocept.reference.collection
import grokcore.component
import six
import zope.interface


class IOperator(zope.interface.Interface):
    """Update operator."""

    def __init__(operand1):
        """Store operand one."""

    def __call__(operand2):
        """Operate `operand2` on `operand1`."""


class Operator(grokcore.component.Adapter):
    """Base class for operators."""

    grokcore.component.implements(IOperator)
    grokcore.component.context(object)

    def __init__(self, operand1):
        self.operand1 = operand1

    def __call__(self, operand2):
        raise NotImplementedError()


class TextAppend(Operator):
    """Append to text."""

    grokcore.component.context(six.text_type)
    grokcore.component.name('append')

    def __call__(self, operand2):
        return self.operand1 + operand2


class Replace(Operator):
    """Replace."""

    grokcore.component.context(zope.interface.Interface)
    grokcore.component.name('replace')

    def __call__(self, operand2):
        return operand2


class NoneAppend(Replace):
    """Append to None."""

    grokcore.component.name('append')


class TextPrepend(Operator):
    """Prepend to text."""

    grokcore.component.context(six.text_type)
    grokcore.component.name('prepend')

    def __call__(self, operand2):
        return operand2 + self.operand1


class NonePrepend(Replace):
    """Prepend to None."""

    grokcore.component.name('prepend')


class RemoveAll(Operator):
    """Remove all occurrences of operand2 from operand1."""

    grokcore.component.context(six.text_type)
    grokcore.component.name('remove-all')

    def __call__(self, operand2):
        return self.operand1.replace(operand2, '')


class NoneRemoveAll(Operator):
    """Remove all for None."""

    grokcore.component.context(zope.interface.Interface)
    grokcore.component.name('remove-all')

    def __call__(self, operand2):
        return self.operand1


class RemoveFirst(Operator):
    """Remove left-most occurrence of operand2 from operand1."""

    grokcore.component.context(six.text_type)
    grokcore.component.name('remove-first')

    def __call__(self, operand2):
        return self.operand1.replace(operand2, '', 1)


class NoneRemoveFirst(NoneRemoveAll):
    """Remove first for None."""

    grokcore.component.name('remove-first')


class RemoveLast(Operator):
    """Remove right-most occurrence of operand2 from operand1."""

    grokcore.component.context(six.text_type)
    grokcore.component.name('remove-last')

    def __call__(self, operand2):
        # [::-1] reverses the string
        return self.operand1[::-1].replace(operand2[::-1], '', 1)[::-1]


class NoneRemoveLast(NoneRemoveAll):
    """Remove last for None."""

    grokcore.component.name('remove-last')


class KeywordOperator(Operator):
    """Base class for keyword operators."""

    grokcore.component.context(gocept.reference.collection.InstrumentedSet)

    def __init__(self, operand1):
        super(KeywordOperator, self).__init__(operand1)
        # convert InstrumentedSet to a set so normal set operations are
        # useable on it
        self.operand1 = set(x for x in self.operand1)


class KeywordUnion(KeywordOperator):
    """Union keywords."""

    grokcore.component.name('union')

    def __call__(self, operand2):
        return self.operand1.union(operand2)


class KeywordDifference(KeywordOperator):
    """Difference keywords."""

    grokcore.component.name('difference')

    def __call__(self, operand2):
        return self.operand1.difference(operand2)


class KeywordIntersection(KeywordOperator):
    """Intersect keywords."""

    grokcore.component.name('intersection')

    def __call__(self, operand2):
        return self.operand1.intersection(operand2)


class KeywordSymmetricDifference(KeywordOperator):
    """Compute symmetric difference of keywords."""

    grokcore.component.name('symmetric_difference')

    def __call__(self, operand2):
        return self.operand1.symmetric_difference(operand2)


class IntAdd(Operator):
    """Add operand2 to operand1 for ints."""

    grokcore.component.context(int)
    grokcore.component.name('add')

    def __call__(self, operand2):
        return self.operand1 + operand2


class DecimalAdd(IntAdd):
    """Add operand2 to operand1 for decimals."""

    grokcore.component.context(decimal.Decimal)


class NoneAdd(Operator):
    """Add for None."""

    grokcore.component.context(zope.interface.Interface)
    grokcore.component.name('add')

    def __call__(self, operand2):
        return operand2


class IntSub(Operator):
    """Substract operand2 from operand1 for ints."""

    grokcore.component.context(int)
    grokcore.component.name('sub')

    def __call__(self, operand2):
        return self.operand1 - operand2


class DecimalSub(IntSub):
    """Substract operand2 from operand1 for decimals."""

    grokcore.component.context(decimal.Decimal)


class NoneSub(Operator):
    """Sub for None."""

    grokcore.component.context(zope.interface.Interface)
    grokcore.component.name('sub')

    def __call__(self, operand2):
        return -operand2


class IntMul(Operator):
    """Multiply operand2 by operand1 for ints."""

    grokcore.component.context(int)
    grokcore.component.name('mul')

    def __call__(self, operand2):
        return self.operand1 * operand2


class DecimalMul(IntMul):
    """Multiply operand2 by operand1 for decimals."""

    grokcore.component.context(decimal.Decimal)


class NoneMul(Operator):
    """Mul for None."""

    grokcore.component.context(zope.interface.Interface)
    grokcore.component.name('mul')

    def __call__(self, operand2):
        return 0


class IntDiv(Operator):
    """Divide operand1 by operand2 for ints."""

    grokcore.component.context(int)
    grokcore.component.name('div')

    def __call__(self, operand2):
        return self.operand1 // operand2


class DecimalDiv(IntDiv):
    """Divide operand1 by operand2 for decimals."""

    grokcore.component.context(decimal.Decimal)


class NoneDiv(Operator):
    """Div for None."""

    grokcore.component.context(zope.interface.Interface)
    grokcore.component.name('div')

    def __call__(self, operand2):
        return 0

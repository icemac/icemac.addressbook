# -*- coding: utf-8 -*-
import decimal
import gocept.reference.collection
import grokcore.component as grok
import six
import zope.interface


class IOperator(zope.interface.Interface):
    """Update operator."""

    def __init__(operand1):
        """Store operand one."""

    def __call__(operand2):
        """Operate `operand2` on `operand1`."""


class Operator(grok.Adapter):
    """Base class for operators."""

    grok.implements(IOperator)
    grok.context(object)

    def __init__(self, operand1):
        self.operand1 = operand1

    def __call__(self, operand2):
        raise NotImplementedError()


class TextAppend(Operator):
    """Append to text."""

    grok.context(six.text_type)
    grok.name('append')

    def __call__(self, operand2):
        return self.operand1 + operand2


class Replace(Operator):
    """Replace."""

    grok.context(zope.interface.Interface)
    grok.name('replace')

    def __call__(self, operand2):
        return operand2


class NoneAppend(Replace):
    """Append to None."""

    grok.name('append')


class TextPrepend(Operator):
    """Prepend to text."""

    grok.context(six.text_type)
    grok.name('prepend')

    def __call__(self, operand2):
        return operand2 + self.operand1


class NonePrepend(Replace):
    """Prepend to None."""

    grok.name('prepend')


class RemoveAll(Operator):
    """Remove all occurrences of operand2 from operand1."""

    grok.context(six.text_type)
    grok.name('remove-all')

    def __call__(self, operand2):
        return self.operand1.replace(operand2, '')


class NoneRemoveAll(Operator):
    """Remove all for None."""

    grok.context(zope.interface.Interface)
    grok.name('remove-all')

    def __call__(self, operand2):
        return self.operand1


class RemoveFirst(Operator):
    """Remove left-most occurrence of operand2 from operand1."""

    grok.context(six.text_type)
    grok.name('remove-first')

    def __call__(self, operand2):
        return self.operand1.replace(operand2, '', 1)


class NoneRemoveFirst(NoneRemoveAll):
    """Remove first for None."""

    grok.name('remove-first')


class RemoveLast(Operator):
    """Remove right-most occurrence of operand2 from operand1."""

    grok.context(six.text_type)
    grok.name('remove-last')

    def __call__(self, operand2):
        # [::-1] reverses the string
        return self.operand1[::-1].replace(operand2[::-1], '', 1)[::-1]


class NoneRemoveLast(NoneRemoveAll):
    """Remove last for None."""

    grok.name('remove-last')


class KeywordOperator(Operator):
    """Base class for keyword operators."""

    grok.context(gocept.reference.collection.InstrumentedSet)

    def __init__(self, operand1):
        super(KeywordOperator, self).__init__(operand1)
        # convert InstrumentedSet to a set so normal set operations are
        # useable on it
        self.operand1 = set(x for x in self.operand1)


class KeywordUnion(KeywordOperator):
    """Union keywords."""

    grok.name('union')

    def __call__(self, operand2):
        return self.operand1.union(operand2)


class KeywordDifference(KeywordOperator):
    """Difference keywords."""

    grok.name('difference')

    def __call__(self, operand2):
        return self.operand1.difference(operand2)


class KeywordIntersection(KeywordOperator):
    """Intersect keywords."""

    grok.name('intersection')

    def __call__(self, operand2):
        return self.operand1.intersection(operand2)


class KeywordSymmetricDifference(KeywordOperator):
    """Compute symmetric difference of keywords."""

    grok.name('symmetric_difference')

    def __call__(self, operand2):
        return self.operand1.symmetric_difference(operand2)


class IntAdd(Operator):
    """Add operand2 to operand1 for ints."""

    grok.context(int)
    grok.name('add')

    def __call__(self, operand2):
        return self.operand1 + operand2


class DecimalAdd(IntAdd):
    """Add operand2 to operand1 for decimals."""

    grok.context(decimal.Decimal)


class NoneAdd(Operator):
    """Add for None."""

    grok.context(zope.interface.Interface)
    grok.name('add')

    def __call__(self, operand2):
        return operand2


class IntSub(Operator):
    """Substract operand2 from operand1 for ints."""

    grok.context(int)
    grok.name('sub')

    def __call__(self, operand2):
        return self.operand1 - operand2


class DecimalSub(IntSub):
    """Substract operand2 from operand1 for decimals."""

    grok.context(decimal.Decimal)


class NoneSub(Operator):
    """Sub for None."""

    grok.context(zope.interface.Interface)
    grok.name('sub')

    def __call__(self, operand2):
        return -operand2


class IntMul(Operator):
    """Multiply operand2 by operand1 for ints."""

    grok.context(int)
    grok.name('mul')

    def __call__(self, operand2):
        return self.operand1 * operand2


class DecimalMul(IntMul):
    """Multiply operand2 by operand1 for decimals."""

    grok.context(decimal.Decimal)


class NoneMul(Operator):
    """Mul for None."""

    grok.context(zope.interface.Interface)
    grok.name('mul')

    def __call__(self, operand2):
        return 0


class IntDiv(Operator):
    """Divide operand1 by operand2 for ints."""

    grok.context(int)
    grok.name('div')

    def __call__(self, operand2):
        return self.operand1 // operand2


class DecimalDiv(IntDiv):
    """Divide operand1 by operand2 for decimals."""

    grok.context(decimal.Decimal)


class NoneDiv(Operator):
    """Div for None."""

    grok.context(zope.interface.Interface)
    grok.name('div')

    def __call__(self, operand2):
        return 0

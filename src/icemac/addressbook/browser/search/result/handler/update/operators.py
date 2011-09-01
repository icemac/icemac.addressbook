# -*- coding: utf-8 -*-
# Copyright (c) 2011 Michael Howitz
# See also LICENSE.txt
import zope.interface
import grokcore.component


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
        raise NotImplementedError


class TextAppend(Operator):
    """Append to text."""

    grokcore.component.context(unicode)
    grokcore.component.name('append')

    def __call__(self, operand2):
        return self.operand1 + operand2


class NoneAppend(Operator):
    """Append to None."""

    grokcore.component.context(zope.interface.Interface)
    grokcore.component.name('append')

    def __call__(self, operand2):
        return operand2


class TextPrepend(Operator):
    """Prepend to text."""

    grokcore.component.context(unicode)
    grokcore.component.name('prepend')

    def __call__(self, operand2):
        return operand2 + self.operand1


class NonePrepend(Operator):
    """Prepend to None."""

    grokcore.component.context(zope.interface.Interface)
    grokcore.component.name('prepend')

    def __call__(self, operand2):
        return operand2


class Replace(Operator):
    """Replace."""

    grokcore.component.context(zope.interface.Interface)
    grokcore.component.name('replace')

    def __call__(self, operand2):
        return operand2


class RemoveAll(Operator):
    """Remove all occurrences of operand2 from operand1."""

    grokcore.component.context(unicode)
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

    grokcore.component.context(unicode)
    grokcore.component.name('remove-first')

    def __call__(self, operand2):
        return self.operand1.replace(operand2, '', 1)


class NoneRemoveFirst(Operator):
    """Remove first for None."""

    grokcore.component.context(zope.interface.Interface)
    grokcore.component.name('remove-first')

    def __call__(self, operand2):
        return self.operand1


class RemoveLast(Operator):
    """Remove right-most occurrence of operand2 from operand1."""

    grokcore.component.context(unicode)
    grokcore.component.name('remove-last')

    def __call__(self, operand2):
        # [::-1] reverses the string
        return self.operand1[::-1].replace(operand2[::-1], '', 1)[::-1]


class NoneRemoveLast(Operator):
    """Remove last for None."""

    grokcore.component.context(zope.interface.Interface)
    grokcore.component.name('remove-last')

    def __call__(self, operand2):
        return self.operand1

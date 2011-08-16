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
    """Append to None"""

    grokcore.component.context(zope.interface.Interface)
    grokcore.component.name('append')

    def __call__(self, operand2):
        return operand2

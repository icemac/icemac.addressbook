# -*- coding: utf-8 -*-
# Copyright (c) 2011 Michael Howitz
# See also LICENSE.txt
from icemac.addressbook.i18n import _
import zope.interface
import grokcore.component
import icemac.addressbook.browser.interfaces


@grokcore.component.adapter(None, ZeroDivisionError)
@grokcore.component.implementer(icemac.addressbook.browser.interfaces.IErrorMessage)
def zero_divisition_error(field, exc):
    return _('Division by zero')


@grokcore.component.adapter(None, Exception)
@grokcore.component.implementer(icemac.addressbook.browser.interfaces.IErrorMessage)
def ordinary_exception(field, exc):
    return _('Unexpected error occurred: ${klass}: ${text}',
             mapping=dict(klass=exc.__class__.__name__, text=exc))

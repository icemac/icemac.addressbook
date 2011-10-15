# -*- coding: utf-8 -*-
# Copyright (c) 2009-2011 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import _
import datetime
import decimal
import gocept.reference.field
import grokcore.component
import icemac.addressbook.browser
import icemac.addressbook.browser.interfaces
import icemac.addressbook.interfaces
import persistent.mapping
import time
import z3c.form.field
import zc.sourcefactory.contextual
import zope.component
import zope.interface
import zope.schema
import zope.security.proxy


# Error renderers


@grokcore.component.adapter(
    None, zope.schema.interfaces.ConstraintNotSatisfied, name="email")
@grokcore.component.implementer(icemac.addressbook.browser.interfaces.IErrorMessage)
def email_constraint_not_satisfield(field, exc):
    value = exc.args[0]
    return _(u'${value} is not a valid e-mail address.',
             mapping=dict(value=value))



def render_error(entity, field_name, exc):
    "Render the error text using the error render adapters."

    # A queryMultiAdapter call with name=None behaves strange: it seems to
    # delete all adapters matching object and interface, so make sure that
    # the name is not None:
    assert field_name is not None

    # There might be errors which cannot be associated with a specific field
    field = ''
    if field_name:
        field = entity.getField(field_name)

    # try named adapter first
    message = zope.component.queryMultiAdapter(
        (field, exc), icemac.addressbook.browser.interfaces.IErrorMessage,
        name=field_name)
    if message is None:
        # fallback to default (unnamed) adapter
        message = zope.component.getMultiAdapter(
            (field, exc), icemac.addressbook.browser.interfaces.IErrorMessage)
    return message

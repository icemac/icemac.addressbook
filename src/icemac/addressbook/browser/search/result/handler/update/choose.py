# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Michael Howitz
# See also LICENSE.txt
from __future__ import absolute_import

from .base import SessionStorageStep
from icemac.addressbook.i18n import _
import icemac.addressbook.fieldsource
import zope.interface
import zope.schema


class IFieldChooser(zope.interface.Interface):
    """List of updateable fields."""

    field = zope.schema.Choice(
        title=_('Which field should be updated?'),
        source=icemac.addressbook.fieldsource.source)


class Field(SessionStorageStep):
    """Step where the user choosed the field he likes to update."""

    interface = IFieldChooser
    label = _(u'Choose field')

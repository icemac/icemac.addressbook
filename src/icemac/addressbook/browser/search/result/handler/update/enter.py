# -*- coding: utf-8 -*-
# Copyright (c) 2011 Michael Howitz
# See also LICENSE.txt
from __future__ import absolute_import

from .base import SessionStorageStep
from icemac.addressbook.i18n import _
import grokcore.component
import icemac.addressbook.browser.wizard
import icemac.addressbook.fieldsource
import icemac.addressbook.sources
import stabledict
import z3c.form.field
import zc.sourcefactory.interfaces
import zc.sourcefactory.source
import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces


class IOperatorsSource(zc.sourcefactory.interfaces.IFactoredSource):
    "Marker interface for a source defining possible operators on a field."


class BaseOperatorsSource(icemac.addressbook.sources.TitleMappingSource):
    """Base class for operator sources."""

    # grokcore.component does not work hier, don't know why
    zope.interface.implementsOnly(IOperatorsSource)


class TextOperatorsSource(BaseOperatorsSource):
    """Operators for Text and TextLine fields."""

    zope.component.adapts(zope.schema.interfaces.IText)

    _default_value = 'append'
    _missing_value = u''
    _mapping = stabledict.StableDict(
        (('prepend', _('prepend new value to existing one')),
         ('replace', _('replace existing value with new one')),
         ('append', _('append new value to existing one')),
         ('remove-all',
            _('remove all occurrences of new value in existing one')),
         ('remove-first',
            _('remove left-most occurrence of new value in existing one')),
         ('remove-last',
            _('remove right-most occurrence of new value in existing one')),
         ))


class BoolOperatorsSource(BaseOperatorsSource):
    """Operators for Bool fields."""

    zope.component.adapts(zope.schema.interfaces.IBool)

    _default_value = 'replace'
    _missing_value = None
    _mapping = stabledict.StableDict(
            (('replace', _('replace existing value with new one')),))


class Value(SessionStorageStep):
    """Step where the user enters the new value."""

    label = _(u'New value')
    fields = z3c.form.field.Fields()

    def update(self):
        session = self.getContent()
        entity, selected_field = icemac.addressbook.fieldsource.untokenize(
            session['field'])
        fields = []
        # We have to support user defined fields here:
        selected_field = zope.schema.interfaces.IField(selected_field)
        source = IOperatorsSource(selected_field)
        field_options = source.factory
        new_value_field = selected_field.__class__(
            title=_('new value'), required=False,
            description=_('This value should be set on each selected person.'),
            missing_value=field_options._missing_value)
        new_value_field.__name__ = 'new_value'
        fields.append(new_value_field)
        operation_field =  zope.schema.Choice(
            title=_('operation'), source=source,
            description=_(
                'What should be done with the current value and the new one?'),
            default=field_options._default_value,)
        operation_field.__name__ = 'operation'
        fields.append(operation_field)
        self.fields = z3c.form.field.Fields(*fields)
        super(Value, self).update()

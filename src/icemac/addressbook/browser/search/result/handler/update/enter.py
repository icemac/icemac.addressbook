# -*- coding: utf-8 -*-
# Copyright (c) 2011 Michael Howitz
# See also LICENSE.txt
from __future__ import absolute_import

from .base import SessionStorageStep
from icemac.addressbook.i18n import _
import decimal
import grokcore.component
import icemac.addressbook.browser.wizard
import icemac.addressbook.fieldsource
import icemac.addressbook.sources
import stabledict
import sys
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


class ReplaceableOperatorsSource(BaseOperatorsSource):
    """Operators for Bool, Choice, Date, Datetime and URI fields."""

    _default_value = 'replace'
    _missing_value = None
    _mapping = stabledict.StableDict(
            (('replace', _('replace existing value with new one')),))


class IntOperatorsSource(BaseOperatorsSource):
    """Operators for Int fields."""

    zope.component.adapts(zope.schema.interfaces.IInt)

    _default_value = 'add'
    _missing_value = 0
    _mapping = stabledict.StableDict(
        (('add', _('add new value to existing one')),
         ('sub', _('substract new value from existing one')),
         ('mul', _('multiply new value by existing one')),
         ('div', _('divide existing value by new one')),
         ('replace', _('replace existing value with new one')),
         ))


class DecimalOperatorsSource(IntOperatorsSource):
    """Operators for Decimal fields."""

    zope.component.adapts(zope.schema.interfaces.IDecimal)
    _missing_value = decimal.Decimal(0)



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
        missing_value = source.factory._missing_value
        parameters = dict(
            title=_('new value'), required=False,
            description=_('This value should be set on each selected person.'),
            missing_value=missing_value)
        if isinstance(selected_field, zope.schema.Choice):
            # Choices need the source of selectable values:
            parameters['source'] = selected_field.source
        # If an IOrderable field has a missing_value which is not None,
        # min, max, and default have to be non-None values, too *sigh*:
        if zope.schema.interfaces.IInt.providedBy(selected_field):
            parameters.update(dict(min=-sys.maxint, max=sys.maxint, default=0))
        if zope.schema.interfaces.IDecimal.providedBy(selected_field):
            max_decimal = decimal.Decimal(sys.maxint)
            # The default value needs to be the same object as missing_value
            # as otherwise z3c.form displayes the default value instead of
            # an empty field:
            parameters.update(dict(min=-max_decimal, max=max_decimal,
                                   default=missing_value))
        new_value_field = selected_field.__class__(**parameters)
        new_value_field.__name__ = 'new_value'
        fields.append(new_value_field)

        operation_field =  zope.schema.Choice(
            title=_('operation'), source=source,
            description=_(
                'What should be done with the current value and the new one?'),
            default=source.factory._default_value,)
        operation_field.__name__ = 'operation'
        fields.append(operation_field)
        self.fields = z3c.form.field.Fields(*fields)
        super(Value, self).update()

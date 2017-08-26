# -*- coding: utf-8 -*-
from .base import SessionStorageStep, get_fieldname_in_session
from icemac.addressbook.i18n import _
import collections
import decimal
import gocept.reference.field
import icemac.addressbook.fieldsource
import icemac.addressbook.sources
import sys
import z3c.form.field
import z3c.form.interfaces
import zc.sourcefactory.interfaces
import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces


class IWillNotGetStripped(zope.schema.interfaces.IText):
    """Suppress stripping of the field value in z3c.form."""


@zope.component.adapter(
    IWillNotGetStripped,
    z3c.form.interfaces.IWidget)
class NotStrippingTextConverter(z3c.form.converter.BaseDataConverter):
    """Since version 3.2.1 of z3c.form text values are stripped.

    This new feature is not wanted here. E. g. we want to be able to add text
    to a field prefixed with a newline.
    """

    _strip_value = False


class IOperatorsSource(zc.sourcefactory.interfaces.IFactoredSource):
    """Marker interface for a source defining possible operators on a field."""


# grokcore.component does not work here, don't know why
@zope.interface.implementer_only(IOperatorsSource)
class BaseOperatorsSource(icemac.addressbook.sources.TitleMappingSource):
    """Base class for operator sources."""


@zope.component.adapter(zope.schema.interfaces.IText)
class TextOperatorsSource(BaseOperatorsSource):
    """Operators for Text and TextLine fields."""

    _default_value = 'append'
    _missing_value = u''
    _mapping = collections.OrderedDict(
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
    _mapping = collections.OrderedDict(
        (('replace', _('replace existing value with new one')),))


@zope.component.adapter(gocept.reference.field.Set)
class KeywordOperatorsSource(BaseOperatorsSource):
    """Operators for keywords."""

    _default_value = 'union'
    _missing_value = set()
    _mapping = collections.OrderedDict((
        ('union', _('append selected keywords to existing ones')),
        ('difference', _('remove selected keywords from existing ones')),
        ('intersection', _(
            'intersection (i. e. keywords which are in selected keywords and '
            'existing ones)')),
        ('symmetric_difference', _(
            'symmetric difference (i. e. keywords which are either in '
            'selected keywords or existing ones but not both)')),
    ))


@zope.component.adapter(zope.schema.interfaces.IInt)
class IntOperatorsSource(BaseOperatorsSource):
    """Operators for Int fields."""

    _default_value = 'add'
    _missing_value = 0
    _mapping = collections.OrderedDict(
        (('add', _('add new value to existing one')),
         ('sub', _('substract new value from existing one')),
         ('mul', _('multiply new value by existing one')),
         ('div', _('divide existing value by new one')),
         ('replace', _('replace existing value with new one')),
         ))


@zope.component.adapter(zope.schema.interfaces.IDecimal)
class DecimalOperatorsSource(IntOperatorsSource):
    """Operators for Decimal fields."""

    _missing_value = decimal.Decimal(0)


class Value(SessionStorageStep):
    """Step where the user enters the new value."""

    title = label = _(u'New value')
    fields = z3c.form.field.Fields()

    def _create_fields(self, session):
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
        if isinstance(selected_field, gocept.reference.field.Set):
            # Keyword field needs its value_type:
            parameters['value_type'] = selected_field.value_type
        # If an IOrderable field has a missing_value which is not None,
        # min, max, and default have to be non-None values, too *sigh*:
        if zope.schema.interfaces.IInt.providedBy(selected_field):
            parameters.update(dict(
                min=-sys.maxsize, max=sys.maxsize, default=0))
        if zope.schema.interfaces.IDecimal.providedBy(selected_field):
            max_decimal = decimal.Decimal(sys.maxsize)
            # The default value needs to be the same object as missing_value
            # as otherwise z3c.form displays the default value instead of
            # an empty field:
            parameters.update(dict(min=-max_decimal, max=max_decimal,
                                   default=missing_value))
        new_value_field = selected_field.__class__(**parameters)
        new_value_field.__name__ = get_fieldname_in_session(session['field'])
        if zope.schema.interfaces.IText.providedBy(new_value_field):
            zope.interface.alsoProvides(new_value_field, IWillNotGetStripped)
        fields.append(new_value_field)
        operation_field = zope.schema.Choice(
            title=_('operation'), source=source,
            description=_(
                'What should be done with the current value and the new one?'),
            default=source.factory._default_value, )
        operation_field.__name__ = 'operation'
        fields.append(operation_field)
        self.fields = z3c.form.field.Fields(*fields)

    def update(self):
        session = self.getContent()
        if 'field' in session:
            # Otherwise the user has selected this step before completing the
            # previous one.
            self._create_fields(session)
        super(Value, self).update()

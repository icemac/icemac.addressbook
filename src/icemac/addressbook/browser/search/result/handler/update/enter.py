from __future__ import absolute_import
from .base import SessionStorageStep
from icemac.addressbook.i18n import _
import grokcore.component
import icemac.addressbook.browser.wizard
import icemac.addressbook.fieldsource
import icemac.addressbook.sources
import stabledict
import z3c.form.field
import zope.interface
import zope.schema


class TextOperationSource(icemac.addressbook.sources.TitleMappingSource):
    _default_value = 'append'
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

text_operation_source = TextOperationSource()


class Value(SessionStorageStep):
    """Step where the user enters the new value."""

    label = _(u'New value')
    fields = z3c.form.field.Fields()

    def update(self):
        session = self.getContent()
        entity, selected_field = icemac.addressbook.fieldsource.untokenize(
            session['field'])
        fields = []
        new_value_field = selected_field.__class__(
            title=_('new value'), required=False,
            description=_('This value should be set on each selected person.'))
        new_value_field.__name__ = 'new_value'
        fields.append(new_value_field)
        operation_field =  zope.schema.Choice(
            # XXX customize source depending on field type.
            title=_('operation'), source=text_operation_source,
            description=_(
                'What should be done with the current value and the new one?'),
                default=text_operation_source.factory._default_value)
        operation_field.__name__ = 'operation'
        fields.append(operation_field)
        self.fields = z3c.form.field.Fields(*fields)
        super(Value, self).update()

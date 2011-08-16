# -*- coding: utf-8 -*-
# Copyright (c) 2011 Michael Howitz
# See also LICENSE.txt
from __future__ import absolute_import

from .base import (
    SessionStorageStep, get_session, get_update_data_session, update_persons)
from icemac.addressbook.i18n import _
import grokcore.component
import icemac.addressbook.browser.personlist
import icemac.addressbook.browser.table
import icemac.addressbook.browser.wizard
import icemac.addressbook.fieldsource
import icemac.addressbook.interfaces
import icemac.addressbook.sources
import stabledict
import transaction
import z3c.form.field
import z3c.table.column
import zope.interface
import zope.schema


class TitleColumn(z3c.table.column.Column):
    """Column wich displays the title of the object."""

    def renderCell(self, person):
        return icemac.addressbook.interfaces.ITitle(person)


class ErrorColumn(z3c.table.column.Column):
    """Column displaying operation and validation errors."""

    def renderCell(self, person):
        # XXX render constraint errors
        return ''

def get_chosen_entity_and_field(request):
    """Returns entity and field objects for chosen field."""
    field_token = get_update_data_session(request)['field']
    return icemac.addressbook.preferences.sources.untokenize(field_token)


class ReviewTable(icemac.addressbook.browser.table.Table):
    """Table containing changed data for review."""

    sortOn = None

    def setUpColumns(self):
        entity, field = get_chosen_entity_and_field(self.request)
        return [
            z3c.table.column.addColumn(
                self, TitleColumn, 'name', weight=1, header=_('name')),
            icemac.addressbook.browser.personlist.createFieldColumn(
                    self, entity, field, 2),
            z3c.table.column.addColumn(
                self, ErrorColumn, 'errors', weight=3, header=_('errors')),
            ]

    @property
    def values(self):
        session = get_session(self.request)
        for person_id in session['person_ids']:
            yield self.context[person_id]


class Result(SessionStorageStep):
    """Step where the user can check the result."""

    label = _(u'Check result')
    fields = z3c.form.field.Fields()
    handleApplyOnComplete = False

    def _update_persons(self):
        """Update the persons as the user seleted it."""
        person_ids = get_session(self.request)['person_ids']
        persons = [self.context[x] for x in person_ids]
        entity, field = get_chosen_entity_and_field(self.request)
        update_data = get_update_data_session(self.request)
        update_persons(persons, entity, field, update_data['operation'],
                       update_data['new_value'])

    def renderResultTable(self):
        self._update_persons()
        # Make sure that changes are not yet persisted:
        transaction.doom()
        table = ReviewTable(self.context, self.request)
        table.update()
        return table.render()

    def doComplete(self, action):
        """Handler for Complete button."""
        # Current transaction is doomed (see renderResultTable), so we have
        # to abort it to make it possible it will get commited at end of
        # request:
        transaction.abort()
        self._update_persons()
        return super(Result, self).doComplete(action)

# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Michael Howitz
# See also LICENSE.txt
from __future__ import absolute_import

from .base import (
    SessionStorageStep, get_update_data_session, update_persons,
    clean_update_data_session, get_fieldname_in_session)
from icemac.addressbook.i18n import _
import icemac.addressbook.browser.personlist
import icemac.addressbook.browser.search.result.handler.base
import icemac.addressbook.browser.table
import icemac.addressbook.fieldsource
import icemac.addressbook.interfaces
import transaction
import z3c.form.field
import z3c.table.column
import zope.i18n


class TitleColumn(z3c.table.column.Column):
    """Column wich displays the title of the object."""

    def renderCell(self, person):
        return icemac.addressbook.interfaces.ITitle(person)


class ErrorColumn(z3c.table.column.Column):
    """Column displaying operation and validation errors."""

    def renderCell(self, person):
        session = get_update_data_session(self.request)
        return zope.i18n.translate(
            session.get('errors', {}).get(person.__name__, ''),
            context=self.request)


def get_chosen_entity_and_field(request):
    """Returns entity and field objects for chosen field."""
    field_token = get_update_data_session(request)['field']
    return icemac.addressbook.fieldsource.untokenize(field_token)


class ReviewTable(icemac.addressbook.browser.table.Table,
                  icemac.addressbook.browser.search.result.handler.base.Base):
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
        return self.persons


class Result(SessionStorageStep,
             icemac.addressbook.browser.search.result.handler.base.Base):
    """Step where the user can check the result."""

    label = _(u'Check result')
    fields = z3c.form.field.Fields()
    handleApplyOnComplete = False

    @property
    def update_data(self):
        return get_update_data_session(self.request)

    def _completeable(self):
        """Tells whether this step is completeable."""
        update_data = self.update_data
        return 'field' in update_data and 'operation' in update_data

    def update(self):
        if self._completeable():
            # Otherwise the user has clicked on this step in navigation before
            # entring data.
            self._update_persons()
            # Make sure that changes are not yet persisted:
            transaction.doom()
        super(Result, self).update()

    def _update_persons(self):
        """Update the persons as the user selected it."""
        entity, field = get_chosen_entity_and_field(self.request)
        fieldname = self.getContent()['field']
        update_data = self.update_data
        errors = update_persons(
            self.persons, entity, field, update_data['operation'],
            update_data[get_fieldname_in_session(fieldname)])
        update_data['errors'] = errors

    def renderResultTable(self):
        table = ReviewTable(self.context, self.request)
        table.update()
        return table.render()

    @property
    def showCompleteButton(self):
        """Complete button condition."""
        if not self._completeable():
            return False
        if self.update_data.get('errors'):
            return False
        return super(Result, self).showCompleteButton

    def doComplete(self, action):
        """Handler for Complete button."""
        # Current transaction is doomed (see renderResultTable), so we have
        # to abort it to make it possible it will get commited at end of
        # request:
        transaction.abort()
        self._update_persons()
        clean_update_data_session(self.request)
        return super(Result, self).doComplete(action)

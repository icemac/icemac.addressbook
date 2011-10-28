# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Michael Howitz
# See also LICENSE.txt
import icemac.addressbook.fieldsource
import icemac.addressbook.interfaces
import icemac.addressbook.utils
import zope.app.appsetup.bootstrap
import zope.preference.default
import zope.preference.interfaces


def add(address_book):
    """Add a default preferences provider to the address book."""
    # Add a default preferences utility on the address book site.
    if icemac.addressbook.utils.utility_locally_registered(
            address_book,
            zope.preference.interfaces.IDefaultPreferenceProvider):
        default_prefs = zope.component.getUtility(
            zope.preference.interfaces.IDefaultPreferenceProvider)
    else:
        default_prefs = zope.app.appsetup.bootstrap.ensureUtility(
            address_book,
            zope.preference.interfaces.IDefaultPreferenceProvider, '',
            zope.preference.default.DefaultPreferenceProvider)

    # Set the defaults for the person list.
    personList = default_prefs.getDefaultPreferenceGroup('personList')
    personList.columns = []
    # The default columns are person last name and person first name.
    person_entity = icemac.addressbook.interfaces.IEntity(
        icemac.addressbook.interfaces.IPerson)
    personList.columns.append(
        icemac.addressbook.fieldsource.tokenize(person_entity, 'last_name'))
    personList.columns.append(
        icemac.addressbook.fieldsource.tokenize(person_entity, 'first_name'))
    personList._p_changed = True
    # The default sort column is person last name.
    personList.order_by = icemac.addressbook.fieldsource.tokenize(
        person_entity, 'last_name')
    # The default sort direction is ascending
    personList.sort_direction = 'ascending'
    personList.batch_size = 20

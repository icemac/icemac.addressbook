# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

import gocept.reference
import zope.annotation.interfaces
import zope.container.btree
import zope.interface
import zope.lifecycleevent
import zope.schema.fieldproperty

import icemac.addressbook.interfaces
import icemac.addressbook.sources

class Person(zope.container.btree.BTreeContainer):
    "A person."

    zope.interface.implements(icemac.addressbook.interfaces.IPerson,
                              icemac.addressbook.interfaces.IPersonDefaults,
                              zope.annotation.interfaces.IAttributeAnnotatable)

    first_name = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPerson['first_name'])
    last_name = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPerson['last_name'])
    birth_date = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPerson['birth_date'])
    sex = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPerson['sex'])
    notes = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPerson['notes'])

    keywords = gocept.reference.ReferenceCollection(ensure_integrity=True)
    default_postal_address = gocept.reference.Reference(ensure_integrity=True)
    default_email_address = gocept.reference.Reference(ensure_integrity=True)
    default_home_page_address = gocept.reference.Reference(
        ensure_integrity=True)
    default_phone_number = gocept.reference.Reference(ensure_integrity=True)


@zope.component.adapter(icemac.addressbook.interfaces.IPerson)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def title(person):
    """Whole name of the person."""
    if not(person.first_name or person.last_name):
        return u'<no name>'
    if not person.first_name:
        if not person.sex:
            return person.last_name
        else:
            return u'%s %s' % (
                icemac.addressbook.sources.salutation_source.factory.
                    getTitle(person.sex),
                person.last_name)
    return u'%s, %s' % (person.last_name, person.first_name)


@zope.component.adapter(icemac.addressbook.interfaces.IPerson,
                        zope.lifecycleevent.IObjectCreatedEvent)
def person_created(person, event):
    """Create initial infrastructure or update existing infrastructure to
    current requirements (using generation)."""
    # Set default values for references as z3c.form accesses the
    # attributes before a value is assigned and gets an AttributeError
    # otherwise.
    if not hasattr(person, 'keywords'):
        person.keywords = set()
    for attrib in ['default_postal_address', 'default_email_address',
                   'default_home_page_address', 'default_phone_number']:
        if not hasattr(person, attrib):
            setattr(person, attrib, None)


class Keywords(object):

    zope.interface.implements(icemac.addressbook.interfaces.IKeywordTitles)
    zope.component.adapts(icemac.addressbook.interfaces.IPerson)

    def __init__(self, context):
        self.context = context

    def get_titles(self):
        return [icemac.addressbook.interfaces.ITitle(x)
                for x in self.context.keywords]

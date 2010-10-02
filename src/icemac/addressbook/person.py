# -*- coding: utf-8 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import gocept.reference
import icemac.addressbook.address
import icemac.addressbook.entities
import icemac.addressbook.interfaces
import zope.annotation.interfaces
import zope.container.btree
import zope.interface
import zope.lifecycleevent
import zope.schema.fieldproperty


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
    notes = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPerson['notes'])

    keywords = gocept.reference.ReferenceCollection(
        'keywords', ensure_integrity=True)
    default_postal_address = gocept.reference.Reference(
        'default_postal_address',ensure_integrity=True)
    default_email_address = gocept.reference.Reference(
        'default_email_address', ensure_integrity=True)
    default_home_page_address = gocept.reference.Reference(
        'default_home_page_address', ensure_integrity=True)
    default_phone_number = gocept.reference.Reference(
        'default_phone_number', ensure_integrity=True)


person_entity = icemac.addressbook.entities.create_entity(
    _(u'person'), icemac.addressbook.interfaces.IPerson, Person)


@zope.component.adapter(icemac.addressbook.interfaces.IPerson)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def title(person):
    """Whole name of the person."""
    if not(person.first_name or person.last_name):
        return u'<no name>'
    if not person.first_name:
        return person.last_name
    return u'%s, %s' % (person.last_name, person.first_name)


def get_default_field(interface):
    "Find the field of a default value attribute on person."
    # XXX use IEntity(interface).taggedValues['default_attrib'] here:
    names_descrs = (
        icemac.addressbook.interfaces.IPersonDefaults.namesAndDescriptions())
    for name, descr in names_descrs:
        if descr.source.factory.interface == interface:
            return icemac.addressbook.interfaces.IPersonDefaults[name]


class PersonDefaultsEntity(icemac.addressbook.entities.Entity):
    "Entity which sorts the fields in IPersonDefaults alike entity order."

    def getRawFields(self):
        name_fields = super(PersonDefaultsEntity, self).getRawFields()
        entity_order = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntityOrder)

        def sortkey((name, field)):
            entity = (
                icemac.addressbook.address.default_attrib_name_to_entity(name))
            return entity_order.get(entity)

        return sorted(name_fields, key=sortkey)


person_defaults_entity = PersonDefaultsEntity(
    _(u'main adresses and numbers'),
    icemac.addressbook.interfaces.IPersonDefaults,
    'icemac.addressbook.person.PersonDefaults')


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

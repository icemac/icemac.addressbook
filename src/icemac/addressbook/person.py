# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Michael Howitz
# See also LICENSE.txt
from icemac.addressbook.i18n import _
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
    icemac.addressbook.schema.createFieldProperties(
        icemac.addressbook.interfaces.IPerson, omit=['keywords'])

    keywords = gocept.reference.ReferenceCollection(
        'keywords', ensure_integrity=True)
    default_postal_address = gocept.reference.Reference(
        'default_postal_address', ensure_integrity=True)
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


def sorted_person_defaults(name_field_tuples):
    """Sorts the `name_field_tuples` as defined in entity order."""
    entity_order = zope.component.getUtility(
        icemac.addressbook.interfaces.IEntityOrder)
    return sorted(
        name_field_tuples,
        key=lambda (name, field): entity_order.get(
            icemac.addressbook.address.default_attrib_name_to_entity(name)))


class PersonDefaultsEntity(icemac.addressbook.entities.Entity):
    "Entity which sorts the fields in IPersonDefaults alike entity order."

    def getRawFields(self, sorted=True):
        name_fields = super(
            PersonDefaultsEntity, self).getRawFields(sorted=False)
        if sorted:
            return sorted_person_defaults(name_fields)
        return name_fields


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


class PersonName(object):

    zope.interface.implements(icemac.addressbook.interfaces.IPersonName)
    zope.component.adapts(icemac.addressbook.interfaces.IPerson)

    def __init__(self, person):
        self.person = person

    def get_name(self):
        values = [self.person.first_name, self.person.last_name]
        result = [x for x in values if x]
        return ' '.join(result)

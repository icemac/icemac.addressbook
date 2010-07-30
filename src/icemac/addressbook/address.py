# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.entities
import icemac.addressbook.interfaces
import persistent
import zope.container.contained
import zope.globalrequest
import zope.interface
import zope.schema.fieldproperty


class PostalAddress(
    persistent.Persistent, zope.container.contained.Contained):
    "A postal address."

    zope.interface.implements(icemac.addressbook.interfaces.IPostalAddress)

    address_prefix = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPostalAddress['address_prefix'])
    street = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPostalAddress['street'])
    city = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPostalAddress['city'])
    zip = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPostalAddress['zip'])
    country = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPostalAddress['country'])


# postal address entity, default_attrib is the name of the attribute
# on IPerson which contains the default postal address.
postal_address_entity = icemac.addressbook.entities.create_entity(
    _(u'postal address'), icemac.addressbook.interfaces.IPostalAddress,
    PostalAddress, default_attrib='default_postal_address')


@zope.component.adapter(icemac.addressbook.interfaces.IPostalAddress)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def postal_address_title(address):
    """Title of a postal address."""
    title = _('none')
    values = [icemac.addressbook.interfaces.ITitle(getattr(address, x))
              for x in ('address_prefix', 'street', 'zip', 'city', 'country')
              if getattr(address, x)]
    if values:
        request = zope.globalrequest.getRequest()
        translated_values = []
        for val in values:
            if isinstance(val, zope.i18nmessageid.Message):
                val = zope.i18n.translate(val, context=request)
            translated_values.append(val)
        title = ', '.join(translated_values)
    return title

class EMailAddress(
    persistent.Persistent, zope.container.contained.Contained):
    """An e-mail address."""

    zope.interface.implements(icemac.addressbook.interfaces.IEMailAddress)

    email = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IEMailAddress['email'])


# e-mail address entity, default_attrib is the name of the attribute
# on IPerson which contains the default e-mail address.
e_mail_address_entity = icemac.addressbook.entities.create_entity(
    _(u'e-mail address'), icemac.addressbook.interfaces.IEMailAddress,
    EMailAddress, default_attrib='default_email_address')


@zope.component.adapter(icemac.addressbook.interfaces.IEMailAddress)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def email_address_title(email):
    """Title of an e-mail address."""
    title = _('none')
    if email.email:
        title = email.email
    return title


class HomePageAddress(
    persistent.Persistent, zope.container.contained.Contained):
    """A home page address."""

    zope.interface.implements(icemac.addressbook.interfaces.IHomePageAddress)

    url = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IHomePageAddress['url'])


# home page address entity, default_attrib is the name of the attribute
# on IPerson which contains the default home page address.
home_page_address_entity = icemac.addressbook.entities.create_entity(
    _(u'home page address'), icemac.addressbook.interfaces.IHomePageAddress,
    HomePageAddress, default_attrib='default_home_page_address')


@zope.component.adapter(icemac.addressbook.interfaces.IHomePageAddress)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def home_page_address_title(hp):
    """Title of a home page address."""
    title = _('none')
    if hp.url:
        title = unicode(hp.url)
    return title


class PhoneNumber(
    persistent.Persistent, zope.container.contained.Contained):
    """A phone number."""

    zope.interface.implements(icemac.addressbook.interfaces.IPhoneNumber)

    number = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPhoneNumber['number'])


# phone number entity, default_attrib is the name of the attribute
# on IPerson which contains the default phone number.
phone_number_entity = icemac.addressbook.entities.create_entity(
    _(u'phone number'), icemac.addressbook.interfaces.IPhoneNumber,
    PhoneNumber, default_attrib='default_phone_number')


@zope.component.adapter(icemac.addressbook.interfaces.IPhoneNumber)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def phone_number_title(tel):
    """Title of a phone number."""
    title = _('none')
    if tel.number:
        title = tel.number
    return title


address_mapping = (
    dict(interface=icemac.addressbook.interfaces.IPostalAddress,
         title=_(u'postal address'),
         prefix='postal_address',
         class_=PostalAddress),
    dict(interface=icemac.addressbook.interfaces.IPhoneNumber,
         title=_(u'phone number'),
         prefix='phone_number',
         class_=PhoneNumber),
    dict(interface=icemac.addressbook.interfaces.IEMailAddress,
         title=_(u'e-mail address'),
         prefix='email_address',
         class_=EMailAddress),
    dict(interface=icemac.addressbook.interfaces.IHomePageAddress,
         title=_(u'home page address'),
         prefix='home_page_address',
         class_=HomePageAddress),
    )


def object_to_prefix(obj):
    """Convert an object to its prefix."""
    for data in address_mapping:
        if data['interface'].providedBy(obj):
            return data['prefix']
    raise KeyError(obj)


def object_to_title(obj):
    """Convert an object to its title."""
    for data in address_mapping:
        if data['interface'].providedBy(obj):
            return data['title']
    raise KeyError(obj)


def object_to_class(obj):
    """Convert an object to its class."""
    for data in address_mapping:
        if data['interface'].providedBy(obj):
            return data['class_']
    raise KeyError(obj)


def prefix_to_class(prefix):
    """Convert a prefix to its class."""
    for address in icemac.addressbook.address.address_mapping:
        if address['prefix'] == prefix:
            return address['class_']
    raise KeyError(prefix)

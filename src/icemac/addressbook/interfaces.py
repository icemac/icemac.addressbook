# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import gocept.country
import gocept.country.db
import gocept.reference.field
import icemac.addressbook.sources
import re
import zope.interface
import zope.schema


class StateWithoutCountryError(zope.schema.ValidationError):
    __doc__ = _("""A country is required to choose a state.""")


class StateCountryMismatchError(zope.schema.ValidationError):
    __doc__ = _(
        "The selected state does not belong to the selected country.")


PACKAGE_ID = 'icemac.addressbook'


class ITitle(zope.interface.Interface):
    """Title of an entity."""

    def __str__():
        """Return the title of the entity."""


class IAddressBook(zope.interface.Interface):
    """An address book."""

    keywords = zope.interface.Attribute(u'keywords collection (IKeywords).')
    principals = zope.interface.Attribute(
        u'zope.app.authentication.interfaces.IInternalPrincipalContainer')
    importer =  zope.interface.Attribute(
        u'icemac.addressbook.importer.interfaces.IImportContainer')
    fields =  zope.interface.Attribute(u'icemac.addressbook.interfaces.IFields')

    title = zope.schema.TextLine(title=_(u'title'))
    notes = zope.schema.Text(title=_(u'notes'), required=False)


class IPerson(zope.interface.Interface):
    """A person."""

    first_name = zope.schema.TextLine(title=_(u'first name'), required=False)
    last_name = zope.schema.TextLine(title=_(u'last name'))
    birth_date = zope.schema.Date(title=_(u'birth date'), required=False)
    sex = zope.schema.Choice(
        title=_(u'sex'), source=icemac.addressbook.sources.SexSource(),
        required=False)
    keywords = gocept.reference.field.Set(
        title=_('keywords'), required=False,
        value_type=zope.schema.Choice(
            title=_('keywords'),
            source=icemac.addressbook.sources.keyword_source))
    notes = zope.schema.Text(title=_(u'notes'), required=False)


class IPostalAddress(zope.interface.Interface):
    """A postal address."""

    kind = zope.schema.Choice(
        title=_(u'kind'), required=False,
        source=icemac.addressbook.sources.work_private_kind_source)
    address_prefix = zope.schema.TextLine(
        title=_(u'address prefix'), required=False,
        description=_(u'e. g. company name or c/o'))
    street = zope.schema.TextLine(title=_(u'street'), required=False)
    city = zope.schema.TextLine(title=_(u'city'), required=False)
    zip = zope.schema.TextLine(title=_(u'zip'), required=False)
    country = zope.schema.Choice(
        title=_(u'country'), source=gocept.country.countries,
        required=False, default=gocept.country.db.Country('DE'))
    state = zope.schema.Choice(
        title=_(u'state'), required=False,
        source=gocept.country.SubdivisionSource(country_code=['DE']))
    notes = zope.schema.Text(title=_(u'notes'), required=False)

    @zope.interface.invariant
    def state_country(obj):
        if not obj.state:
            return None
        if obj.state and not obj.country:
            raise StateWithoutCountryError(obj)
        if obj.country.alpha2 != obj.state.country_code:
            raise StateCountryMismatchError(obj)


class IEMailAddress(zope.interface.Interface):
    """An e-mail address."""

    kind = zope.schema.Choice(
        title=_(u'kind'), required=False,
        source=icemac.addressbook.sources.work_private_kind_source)
    email = zope.schema.TextLine(
        title=_(u'e-mail address'), required=False,
        constraint=re.compile(
            "^[=+A-Za-z0-9_.-]+@([A-Za-z0-9_\-]+\.)+[A-Za-z]{2,6}$").match)
    notes = zope.schema.Text(title=_(u'notes'), required=False)


class IHomePageAddress(zope.interface.Interface):
    """A home page address."""

    kind = zope.schema.Choice(
        title=_(u'kind'), required=False,
        source=icemac.addressbook.sources.work_private_kind_source)
    url = zope.schema.URI(title=_(u'URL'), required=False)
    notes = zope.schema.Text(title=_(u'notes'), required=False)


class IPhoneNumber(zope.interface.Interface):
    """A phone number."""

    kind = zope.schema.Choice(
        title=_(u'kind'), required=False,
        source=icemac.addressbook.sources.phone_number_kind_source)
    number = zope.schema.TextLine(title=_(u'number'), required=False)
    notes = zope.schema.Text(title=_(u'notes'), required=False)


class IPersonDefaults(zope.interface.Interface):
    """Default addresses, phone numbers etc."""

    default_postal_address = zope.schema.Choice(
        title=_(u'main postal address'),
        source=icemac.addressbook.sources.ContextByInterfaceSource(
            IPostalAddress))
    default_phone_number = zope.schema.Choice(
        title=_(u'main phone number'),
        source=icemac.addressbook.sources.ContextByInterfaceSource(
            IPhoneNumber))
    default_email_address = zope.schema.Choice(
        title=_(u'main e-mail address'),
        source=icemac.addressbook.sources.ContextByInterfaceSource(
            IEMailAddress))
    default_home_page_address = zope.schema.Choice(
        title=_(u'main home page address'),
        source=icemac.addressbook.sources.ContextByInterfaceSource(
            IHomePageAddress))


class IKeywords(zope.interface.Interface):
    """Collection of keywords."""

    def get_keywords():
        """Get the keywords in the collection."""

    def get_keyword_by_title(title, default=None):
        "Get the keyword with the given title or `default`."


class IKeywordTitles(zope.interface.Interface):
    """Collection of keywords titles."""

    def get_titles():
        """Get the titles of the keywords in the collection."""


class IKeyword(zope.interface.Interface):
    """A keyword."""

    title = zope.schema.TextLine(title=_(u'keyword'))
    notes = zope.schema.Text(title=_(u'notes'), required=False)


class IFields(zope.interface.Interface):
    """Predefined and user defined schema fields of objects."""

    def getFieldsInOrder(interface):
        "Get ordered name, field tuples of the schema fields of an interface."

    def getFieldValuesInOrder(interface):
        """Get ordered list of the schema fields of an interface."""


class IField(zope.interface.Interface):
    """User defined field."""

    type = zope.schema.Choice(
        title=_(u'type'),
        source=icemac.addressbook.sources.FieldTypeSource())
    title = zope.schema.TextLine(title=_(u'title'))
    values = zope.schema.List(
        title=_(u'values'), unique=True, required=False,
        value_type=zope.schema.TextLine(title=_(u'value')))

    order = zope.schema.Float(title=u'order position')

    @zope.interface.invariant
    def choice_type_needs_values(field):
        if field.type == u'Choice' and not field.values:
            raise zope.interface.Invalid(
                _(u'type "choice" requires values.'))

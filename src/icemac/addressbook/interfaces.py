# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
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


PACKAGE_ID = 'icemac.addressbook'
ENTITIES = 'entites_namespace'

class ITitle(zope.interface.Interface):
    """Title of an entity."""

    def __str__():
        """Return the title of the entity."""


class IAddressBook(zope.interface.Interface):
    """An address book."""

    keywords = zope.interface.Attribute(
        u'icemac.addressbook.interfaces.IKeywords')
    principals = zope.interface.Attribute(
        u'zope.app.authentication.interfaces.IInternalPrincipalContainer')
    importer =  zope.interface.Attribute(
        u'icemac.addressbook.importer.interfaces.IImportContainer')
    entities =  zope.interface.Attribute(
        u'icemac.addressbook.interfaces.IEntities')
    orders = zope.interface.Attribute(
        u'icemac.addressbook.interfaces.IOrderStorage')

    title = zope.schema.TextLine(title=_(u'title'))


class IPerson(zope.interface.Interface):
    """A person."""

    first_name = zope.schema.TextLine(title=_(u'first name'), required=False)
    last_name = zope.schema.TextLine(title=_(u'last name'))
    birth_date = zope.schema.Date(title=_(u'birth date'), required=False)
    keywords = gocept.reference.field.Set(
        title=_('keywords'), required=False,
        value_type=zope.schema.Choice(
            title=_('keywords'),
            source=icemac.addressbook.sources.keyword_source))
    notes = zope.schema.Text(title=_(u'notes'), required=False)


class IPostalAddress(zope.interface.Interface):
    """A postal address."""

    address_prefix = zope.schema.TextLine(
        title=_(u'address prefix'), required=False,
        description=_(u'e. g. company name or c/o'))
    street = zope.schema.TextLine(title=_(u'street'), required=False)
    city = zope.schema.TextLine(title=_(u'city'), required=False)
    zip = zope.schema.TextLine(title=_(u'zip'), required=False)
    country = zope.schema.Choice(
        title=_(u'country'), source=gocept.country.countries,
        required=False, default=gocept.country.db.Country('DE'))


class IEMailAddress(zope.interface.Interface):
    """An e-mail address."""

    email = zope.schema.TextLine(
        title=_(u'e-mail address'), required=False,
        constraint=re.compile(
            "^[=+A-Za-z0-9_.-]+@([A-Za-z0-9_\-]+\.)+[A-Za-z]{2,6}$").match)


class IHomePageAddress(zope.interface.Interface):
    """A home page address."""

    url = zope.schema.URI(title=_(u'URL'), required=False)


class IPhoneNumber(zope.interface.Interface):
    """A phone number."""

    number = zope.schema.TextLine(title=_(u'number'), required=False)


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


class IEntities(zope.interface.Interface):
    """Entities in the address book."""

    def getAllEntities():
        """Get an iterable of all known entities."""


class IEntity(zope.interface.Interface):
    """Entity in the address book."""

    title = zope.schema.TextLine(
        title=u"title of the entity", required=False)
    interface = zope.schema.InterfaceField(title=u"interface")
    class_name = zope.schema.DottedName(
        title=u"dotted name of the class", required=False)

    name = zope.interface.Attribute(
        "Uniqe name of the entity which only contains letters.")
    tagged_values = zope.interface.Attribute(
        "Dict of tagged values of the entity.")

    def getField(field_name):
        """Get a zope.schema field by its name."""

    def getRawFields():
        """Get ordered name, field tuples of the schema fields on the entity.

        Returnes static (zope.schema) and user defined (IField) fields.

        """

    def getFieldsInOrder():
        """Get ordered name, field tuples of the schema fields on the entity.

        Converts user defined fields (see IField) into zope.schema fields.

        """

    def getFieldValuesInOrder():
        """Get ordered list of the schema fields on the entity.

        Converts user defined fields (see IField) into zope.schema fields.

        """

    def getClass():
        """Get the class object for `self.class_name`."""


class IField(zope.interface.Interface):
    """User defined field."""

    __name__ = zope.interface.Attribute('internal field name')

    type = zope.schema.Choice(
        title=_(u'type'),
        source=icemac.addressbook.sources.FieldTypeSource())
    title = zope.schema.TextLine(title=_(u'title'))
    values = zope.schema.List(
        title=_(u'choice field values'), unique=True, required=False,
        value_type=zope.schema.TextLine(title=_(u'value')))
    notes = zope.schema.Text(title=_(u'notes'), required=False)

    @zope.interface.invariant
    def choice_type_needs_values(field):
        if field.type == u'Choice' and not field.values:
            raise zope.interface.Invalid(
                _(u'type "choice" requires at least one field value.'))


class IMayHaveUserFields(zope.interface.Interface):
    """Marker interface: Object may have user defined fields."""


class IUserFieldStorage(zope.interface.Interface):
    """Storage for user defined field values."""


class IOrderStorageRead(zope.interface.Interface):
    """Storage of orders of objects. (read only methods)"""

    def namespaces():
        """Get an iterable of the known namespaces."""

    def get(obj, namespace):
        """Get the index of the object in the list.

        Raises a KeyError when the object is not in the list.
        """

    def __iter__(namespace):
        """Iterate over the list of a namespace."""


class IOrderStorageWrite(zope.interface.Interface):
    """Storage of orders of objects. (write methods)"""

    def add(obj, namespace):
        """Add an object to the order for a namespace.

        When the namespace does not exist, it gets created.
        New objects are added at the end of the list.
        When the object is already in the list it is not added again and
        does not change its position.
        """

    def remove(obj, namespace):
        """Remove the object from the order of a namespace.

        Raises a ValueError when the object is not in the list.
        Raises a KeyError when the namespace does not exist.
        """

    def up(obj, namespace):
        """Move the object one position up in the list.

        When it is already the first one a ValueError is raised.
        """

    def down(obj, namespace):
        """Move the object one position down in the list.

        When it is already the last one a ValueError is raised.
        """

class IOrderStorage(IOrderStorageRead, IOrderStorageWrite):
    """Storage of orders of objects."""

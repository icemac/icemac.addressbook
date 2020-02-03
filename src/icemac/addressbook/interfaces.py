# -*- coding: latin-1 -*-
from icemac.addressbook.i18n import _
import collections
import datetime
import gocept.country
import gocept.country.db
import gocept.reference.field
import icemac.addressbook.sources
import pytz
import re
import zc.sourcefactory.basic
import zc.sourcefactory.contextual
import zc.sourcefactory.source
import zope.catalog.interfaces
import zope.component
import zope.interface
import zope.schema


PACKAGE_ID = 'icemac.addressbook'
ENTITIES = 'entites_namespace'
FIELD_NS_PREFIX = 'fields-'
DEFAULT_FAVICON = '/++resource++img/favicon-red.ico'
DEFAULT_STARTPAGE_DATA = (
    'icemac.addressbook.interfaces.IAddressBook', 'welcome.html')
MIN_SUPPORTED_DATE = datetime.date(1900, 1, 1)


class ITitle(zope.interface.Interface):
    """Title of an entity."""

    def __str__():
        """Return the title of the entity."""


class IImageSource(zope.interface.Interface):
    """Marker interface for a source which uses images as titles.

    Title needs to be the URL of the image.

    """


class IFaviconData(zope.interface.Interface):
    """Data of a favicon."""

    path = zope.interface.Attribute('Path to be used in URL.')
    preview_path = zope.interface.Attribute('Path to be used in preview.')


class FaviconSource(icemac.addressbook.sources.TitleMappingSource):
    """Source containing possbile favicons."""

    @zope.interface.implementer(IImageSource)
    class source_class(zc.sourcefactory.source.FactoredSource):
        """We need the interface to register a widget for it."""

    @property
    def _mapping(self):
        data = [(x.path, x.preview_path)
                for x in zope.component.subscribers((self, ), IFaviconData)]
        if not data:
            # We are at import time, so the subscribers are not yet set up
            # but IAddressBook.favicon checks if the default value is valid:
            data = [(DEFAULT_FAVICON, DEFAULT_FAVICON)]
        return collections.OrderedDict(sorted(data))


favicon_source = FaviconSource()


class IStartpageData(zope.interface.Interface):
    """Data of a possible startpage after login."""

    iface_name = zope.interface.Attribute(
        'Dotted name to an interface to get the object those URL should '
        'be computed.')
    view = zope.interface.Attribute(
        'Name of the view to be displayed on the object.')
    title = zope.interface.Attribute('i18n message id for display in UI')


class StartpageSource(icemac.addressbook.sources.TitleMappingSource):
    """Source containing possbile startpages to be shown after login."""

    @property
    def _mapping(self):
        data = [((x.iface_name, x.view), x.title)
                for x in zope.component.subscribers(
                    (self, ), IStartpageData)]
        if not data:
            # We are at import time, so the subscribers are not yet set up
            # but IAddressBook.startpage checks if the default value is
            # valid:
            data = [(DEFAULT_STARTPAGE_DATA, u'')]
        return collections.OrderedDict(sorted(data))

    def getToken(self, value):
        return str(value)


startpage_source = StartpageSource()


class TimeZones(icemac.addressbook.sources.TitleMappingSource):
    """Source of all available time zones."""

    _mapping = collections.OrderedDict(((x, x) for x in pytz.common_timezones))


time_zones = TimeZones()


class IAddressBook(zope.interface.Interface):
    """An address book."""

    archive = zope.interface.Attribute(
        u'icemac.addressbook.interfaces.IArchive')
    keywords = zope.interface.Attribute(
        u'icemac.addressbook.interfaces.IKeywords')
    principals = zope.interface.Attribute(
        u'zope.pluggableauth.plugins.principalfolder.'
        u'IInternalPrincipalContainer')
    importer = zope.interface.Attribute(
        u'icemac.ab.importer.interfaces.IImportContainer')
    entities = zope.interface.Attribute(
        u'icemac.addressbook.interfaces.IEntities')
    orders = zope.interface.Attribute(
        u'icemac.addressbook.interfaces.IOrderStorage')

    title = zope.schema.TextLine(title=_(u'title'))
    favicon = zope.schema.Choice(
        title=_('favicon'),
        source=favicon_source,
        default=DEFAULT_FAVICON)

    deselected_tabs = zope.schema.Set(
        title=_('Deselected tabs'),
        description=_(
            'The tabs selected here are not shown in the navigation.'
            ' Deselecting a tab can mean to disable the whole feature.'),
        default=set(),
        value_type=zope.schema.Choice(
            title=_('Deselected tabs'),
            source='tabs_source'))

    startpage = zope.schema.Choice(
        title=_('start page after log-in'),
        source=startpage_source,
        default=DEFAULT_STARTPAGE_DATA)

    time_zone = zope.schema.Choice(
        title=_('Time zone'),
        description=_('Fallback in case a user has not set up his personal '
                      'time zone in the preferences.'),
        source=time_zones, default='UTC')


class IKeywords(zope.interface.Interface):
    """Collection of keywords."""

    def get_keywords():
        """Get an iterable of the keywords in the collection."""

    def get_keyword_by_title(title, default=None):
        """Get the keyword with the given title or `default`."""


class IKeywordTitles(zope.interface.Interface):
    """Collection of keywords titles."""

    def get_titles():
        """Get the titles of the keywords in the collection."""


class IKeyword(zope.interface.Interface):
    """A keyword."""

    title = zope.schema.TextLine(title=_(u'keyword'))


class KeywordSource(zc.sourcefactory.basic.BasicSourceFactory):
    """Source of all keywords in the address book."""

    def getValues(self):
        keywords = zope.component.getUtility(IKeywords)
        return sorted(keywords.get_keywords(), key=lambda x: x.title.lower())

    def getTitle(self, value):
        return value.title


keyword_source = KeywordSource()


class ISchemaProvider(zope.interface.Interface):
    """Object provides a schema."""

    schema = zope.interface.Attribute('Interface provided by the object.')


class ISchemaName(zope.interface.Interface):
    """Schema name of an entity to be added to the catalog."""

    schema_name = zope.interface.Attribute('Unicode value of the schema name.')


class ContextByInterfaceSource(
        zc.sourcefactory.contextual.BasicContextualSourceFactory):
    """Source to select objects from context container by a given interface."""

    def __init__(self, interface):
        super(ContextByInterfaceSource, self).__init__()
        self.interface = interface

    def getValues(self, context):
        for value in context.values():
            if self.interface.providedBy(value):
                yield value

    def getTitle(self, context, value):
        return ITitle(value)


class IPersonName(zope.interface.Interface):
    """Name of a person."""

    first_name = zope.schema.TextLine(title=_(u'first name'), required=False)
    last_name = zope.schema.TextLine(title=_(u'last name'))

    def get_name():
        """Return first name and last name of the person.

        Names are separated by a space.
        """


class IPersonData(zope.interface.Interface):
    """Data of a person."""

    birth_date = zope.schema.Date(
        title=_(u'birth date'), required=False, min=MIN_SUPPORTED_DATE)
    keywords = gocept.reference.field.Set(
        title=_('keywords'), required=False,
        value_type=zope.schema.Choice(
            title=_('keywords'),
            source=keyword_source))
    notes = zope.schema.Text(title=_(u'notes'), required=False)


class IPerson(IPersonName, IPersonData):
    """A person."""


class IPersonArchiving(zope.interface.Interface):
    """Methods regarding archiving of a person."""

    def archive():
        """Move the person to the archive."""


class IPersonUnarchiving(zope.interface.Interface):
    """Methods regarding unarchiving of a person."""

    def unarchive():
        """Move the person from the archive back to the person list."""


class IArchivalData(zope.interface.Interface):
    """Data of the archival of a person."""

    archival_date = zope.schema.Datetime(
        title=_('archival date'),
        description=_('Date when the person was archived.'))

    archived_by = zope.schema.TextLine(
        title=_('archived by'))


class IArchivedPerson(
        IPerson,
        IArchivalData,
        zope.catalog.interfaces.INoAutoIndex,
        zope.catalog.interfaces.INoAutoReindex):
    """A person who has been archived."""


class IPersonEntity(zope.interface.Interface):
    """Entity of a person."""


class IPostalAddress(IPersonEntity):
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


class IEMailAddress(IPersonEntity):
    """An e-mail address."""

    email = zope.schema.TextLine(
        title=_(u'e-mail address'), required=False,
        constraint=re.compile(
            r"^[/$!%=+A-Za-z0-9_.-]+@([A-Za-z0-9_\-]+\.)+[A-Za-z]{2,6}$"
        ).match)


class IHomePageAddress(IPersonEntity):
    """A home page address."""

    url = zope.schema.URI(title=_(u'URL'), required=False)


class IPhoneNumber(IPersonEntity):
    """A phone number."""

    number = zope.schema.TextLine(title=_(u'number'), required=False)


class IPersonDefaults(zope.interface.Interface):
    """Default addresses, phone numbers etc."""

    default_postal_address = zope.schema.Choice(
        title=_(u'main postal address'),
        source=ContextByInterfaceSource(IPostalAddress))
    default_phone_number = zope.schema.Choice(
        title=_(u'main phone number'),
        source=ContextByInterfaceSource(IPhoneNumber))
    default_email_address = zope.schema.Choice(
        title=_(u'main e-mail address'),
        source=ContextByInterfaceSource(IEMailAddress))
    default_home_page_address = zope.schema.Choice(
        title=_(u'main home page address'),
        source=ContextByInterfaceSource(IHomePageAddress))


class IEntities(zope.interface.Interface):
    """Entities in the address book."""

    def getEntities(sorted=True):
        """Get an iterable of all known entities.

        When `sorted` is True, order them as defined in IEntityOrder.

        """

    def getMainEntities(sorted=True):
        """Get an iterable of the most important entities.

        When `sorted` is True, order them as defined in IEntityOrder.

        """


class IEntityRead(zope.interface.Interface):
    """Entity in the address book. (Read only part of the interface.)"""

    title = zope.schema.TextLine(
        title=u"title of the entity", required=False)
    interface = zope.schema.InterfaceField(title=u"interface")
    class_name = zope.schema.DottedName(
        title=u"dotted name of the class", required=False)

    name = zope.interface.Attribute(
        "Uniqe name of the entity which only contains letters.")
    tagged_values = zope.interface.Attribute(
        "Dict of tagged values of the entity.")
    order_storage_namespace = zope.interface.Attribute(
        "Get the name space used in the order storage.")

    def getRawField(field_name):
        """Get a field by its name. (Without any conversion.)"""

    def getField(field_name):
        """Get a zope.schema field by its name.

        When the field is a user defined one it gets converted to a zope.schema
        field.
        """

    def getFieldOrder():
        """Get the ordered names of the fields.

        Caution: This method only returns the names for the fields which are
        known in the field order!
        """

    def getRawFields(sorted=True):
        """Get (name, field) tuples of the schema fields on the entity.

        When `sorted` is true the fields are sorted using the field order.

        Returns static (zope.schema) and user defined (IField) fields.

        """

    def getFields(sorted=True):
        """Get (name, field) tuples of the schema fields on the entity.

        When `sorted` is true the fields are sorted using the field order.

        Converts user defined fields (see IField) into zope.schema fields.

        """

    def getFieldValues(sorted=True):
        """Get list of the schema fields on the entity.

        When `sorted` is true the fields are sorted using the field order.

        Converts user defined fields (see IField) into zope.schema fields.

        """

    def getClass():
        """Get the class object for `self.class_name`."""


class IEntityWrite(zope.interface.Interface):
    """Entity in the address book. (Write part of the interface.)"""

    def addField(field):
        """Add a user defined field to the entity.

        Returns the name of the created field.

        """

    def removeField(field):
        """Remove a user defined field from the entity."""

    def setFieldOrder(field_names):
        """Update the order of the fields like in `field_names`.

        field_names ... list of the names of the fields as returned by
                        `getFields`.

        Field names which do not belong to the entity are omitted.
        """


class IEntity(IEntityRead, IEntityWrite):
    """Entity in the address book."""


class IEditableEntity(IEntity):
    """Special entity which is editable.

    This means that new fields can be added and the fields can be sorted.

    """


class IField(zope.interface.Interface):
    """User defined field."""

    __name__ = zope.interface.Attribute('internal field name')
    interface = zope.interface.Attribute('interface the field belongs to')

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

    def isFirst(obj, namespace):
        """Tell whether `obj` is the first object in the list.

        Raises a KeyError when the object is not in the list.
        """

    def isLast(obj, namespace):
        """Tell whether `obj` is the last object in the list.

        Raises a KeyError when the object is not in the list.
        """

    def byNamespace(namespace):
        """List of the objects registered for the namespace."""


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

    def truncate(namespace):
        """Remove all objects from the order of a namespace.

        Does nothing when the namespace is not known.
        """

    def up(obj, namespace, delta=1):
        """Move the object one position up in the list.

        `delta` describes the number of positions to move.

        When it would be moved beyond the beginning of the list a
        ValueError is raised.
        """

    def down(obj, namespace, delta=1):
        """Move the object one position down in the list.

        `delta` describes the number of positions to move.

        When it would be moved beyond the end of the list a ValueError is
        raised.
        """


class IOrderStorage(IOrderStorageRead, IOrderStorageWrite):
    """Storage of orders of objects."""


class IEntityOrder(zope.interface.Interface):
    """Order of entities."""

    def get(entity):
        """Get the index of the entity in the entity order.

        Raises a KeyError when the entity is not known.
        """

    def isFirst(entity):
        """Tell whether `entity` comes first in the entity order.

        Raises a KeyError when the entity is not known.
        """

    def isLast(entity):
        """Tell whether `entity` comes last in the entity order.

        Raises a KeyError when the entity is not known.
        """

    def __iter__():
        """Iterate over the entities sorted by order."""

    def up(entity, delta=1):
        """Move the entity one position up in the entity order.

        `delta` describes the number of positions to move.

        When the entity would be moved beyond the beginning of the entity
        order a ValueError is raised.
        """

    def down(entity, delta=1):
        """Move the entity one position down in the entity order.

        `delta` describes the number of positions to move.

        When it would be moved beyond the end of the entity order a
        ValueError is raised.
        """


class IArchive(zope.interface.Interface):
    """Container of elements which are neither changeable nor searchable."""


class IFieldCustomization(zope.interface.Interface):
    """Custom date for schema fields to be shown in the UI."""

    def set_value(field, kind, label):
        """Set a new value of type kind for the given field.

        kind … either u'label' or u'description'

        Use `None` as value of `label` to delete the stored custom value.
        """

    def get_value(field, kind):
        """Get the stored value of type kind for the field.

        kind … either u'label' or u'description'

        If no custom value is stored, a KeyError is raised.
        """

    def query_value(field, kind):
        """Get the stored value of type kind for the field.

        kind … either u'label' or u'description'

        If no custom value is stored, return the default value.
        """

    def default_value(field, kind):
        """Get the default label for the field."""


class IMayHaveCustomizedPredfinedFields(zope.interface.Interface):
    """Marker interface for objects those pre-defined fields my be customized.

    This is only relevant for pre-defined fields as the user-defined ones
    already have user defined data.
    """

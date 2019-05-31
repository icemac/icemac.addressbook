# -*- coding: utf-8 -*-
from icemac.addressbook.i18n import _
from icemac.addressbook.metadata.subscriber import set_current_princial_id
import contextlib
import gocept.reference
import icemac.addressbook.address
import icemac.addressbook.entities
import icemac.addressbook.interfaces
import zope.annotation.interfaces
import zope.catalog.catalog
import zope.container.btree
import zope.copypastemove.interfaces
import zope.interface
import zope.intid.interfaces
import zope.lifecycleevent


PERMS_NEEDED_IN_ARCHIVE = (
    'icemac.addressbook.ViewEMailAddress',
    'icemac.addressbook.ViewFile',
    'icemac.addressbook.ViewHomePageAddress',
    'icemac.addressbook.ViewPerson',
    'icemac.addressbook.ViewPersonName',
    'icemac.addressbook.ViewPhoneNumber',
    'icemac.addressbook.ViewPostalAddress',
)
PERMS_DENIED_IN_ARCHIVE = (
    'icemac.addressbook.ArchivePerson',
    'icemac.addressbook.ClonePerson',
    'icemac.addressbook.ExportPerson',
    'icemac.addressbook.EditEMailAddress',
    'icemac.addressbook.EditFile',
    'icemac.addressbook.EditHomePageAddress',
    'icemac.addressbook.EditPerson',
    'icemac.addressbook.EditPersonName',
    'icemac.addressbook.EditPhoneNumber',
    'icemac.addressbook.EditPostalAddress',
    'icemac.addressbook.AddEMailAddress',
    'icemac.addressbook.AddFile',
    'icemac.addressbook.AddHomePageAddress',
    'icemac.addressbook.AddPhoneNumber',
    'icemac.addressbook.AddPostalAddress',
)
ROLES_WHO_HAVE_EDIT_PERMISSIONS = (
    'icemac.addressbook.global.Administrator',
    'icemac.addressbook.global.Editor',
)
ROLES_WHO_HAVE_PERMISSIONS_IN_ARCHIVE = (
    'icemac.addressbook.global.Archivist',
    'icemac.addressbook.global.ArchiveVisitor',
)

person_schema = icemac.addressbook.interfaces.IPerson


@contextlib.contextmanager
def default_attribs_set_aside(person):
    """Remove references to sub-objects and restore them afterwards.

    This is needed because with these references `person` cannot be moved.
    """
    defaults = {}
    for attrib in icemac.addressbook.interfaces.IPersonDefaults.names():
        defaults[attrib] = getattr(person, attrib)
        setattr(person, attrib, None)

    try:
        yield
    finally:
        for attrib, value in defaults.items():
            setattr(person, attrib, value)


@zope.interface.implementer(
    person_schema,
    icemac.addressbook.interfaces.IPersonDefaults,
    icemac.addressbook.interfaces.IPersonArchiving,
    icemac.addressbook.interfaces.IPersonUnarchiving,
    icemac.addressbook.interfaces.ISchemaProvider,
    icemac.addressbook.interfaces.IMayHaveCustomizedPredfinedFields,
    zope.annotation.interfaces.IAttributeAnnotatable,
)
class Person(zope.container.btree.BTreeContainer):
    """A person."""

    archived_by = None
    schema = person_schema

    zope.schema.fieldproperty.createFieldProperties(
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

    def get_name(self):
        values = [self.first_name, self.last_name]
        result = [x for x in values if x]
        return ' '.join(result)

    def archive(self):
        """Move the person to the archive."""
        # Remove references to sub-objects because with these references
        # the person cannot be moved. They are restored after the move.
        with default_attribs_set_aside(self):
            zope.copypastemove.interfaces.IObjectMover(self).moveTo(
                icemac.addressbook.interfaces.IArchive(None))
            zope.interface.alsoProvides(
                self, icemac.addressbook.interfaces.IArchivedPerson)

        rpm = zope.securitypolicy.interfaces.IRolePermissionManager(self)
        for perm in PERMS_NEEDED_IN_ARCHIVE:
            for role in ROLES_WHO_HAVE_PERMISSIONS_IN_ARCHIVE:
                rpm.grantPermissionToRole(perm, role)
        for role in ROLES_WHO_HAVE_EDIT_PERMISSIONS:
            for perm in PERMS_DENIED_IN_ARCHIVE:
                rpm.denyPermissionToRole(perm, role)
        self.archival_date = zope.dublincore.timeannotators._now()
        set_current_princial_id(
            self, 'archived_by', icemac.addressbook.interfaces.IArchivalData)
        # uncatalog the person
        event = zope.intid.interfaces.IntIdRemovedEvent(self, None)
        zope.catalog.catalog.unindexDocSubscriber(event)

    def unarchive(self):
        """Move the person out of the archive.

        May only be called on a person in the archive.
        """
        with default_attribs_set_aside(self):
            zope.copypastemove.interfaces.IObjectMover(self).moveTo(
                icemac.addressbook.interfaces.IAddressBook(None))
            zope.interface.noLongerProvides(
                self, icemac.addressbook.interfaces.IArchivedPerson)

        rpm = zope.securitypolicy.interfaces.IRolePermissionManager(self)
        for perm in PERMS_NEEDED_IN_ARCHIVE:
            for role in ROLES_WHO_HAVE_PERMISSIONS_IN_ARCHIVE:
                rpm.denyPermissionToRole(perm, role)
        for role in ROLES_WHO_HAVE_EDIT_PERMISSIONS:
            for perm in PERMS_DENIED_IN_ARCHIVE:
                rpm.grantPermissionToRole(perm, role)
        self.archival_date = None
        self.archived_by = None
        # re-catalog the person
        event = zope.intid.interfaces.IntIdAddedEvent(self, None)
        zope.catalog.catalog.indexDocSubscriber(event)


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
    """Find the field of a default value attribute on person."""
    field_name = icemac.addressbook.interfaces.IEntity(
        interface).tagged_values['default_attrib']
    return icemac.addressbook.interfaces.IPersonDefaults[field_name]


def sorted_person_defaults(name_field_tuples):
    """Sort the `name_field_tuples` as defined in entity order."""
    entity_order = zope.component.getUtility(
        icemac.addressbook.interfaces.IEntityOrder)
    return sorted(
        name_field_tuples,
        key=lambda value: entity_order.get(
            icemac.addressbook.address.default_attrib_name_to_entity(
                value[0])))


class PersonDefaultsEntity(icemac.addressbook.entities.Entity):
    """Entity which sorts the fields in IPersonDefaults alike entity order."""

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


@zope.component.adapter(icemac.addressbook.interfaces.IPerson)
@zope.interface.implementer(icemac.addressbook.interfaces.IKeywordTitles)
class Keywords(object):

    def __init__(self, context):
        self.context = context

    def get_titles(self):
        return [icemac.addressbook.interfaces.ITitle(x)
                for x in self.context.keywords]

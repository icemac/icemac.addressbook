from icemac.addressbook.interfaces import IArchivedPerson
from icemac.addressbook.interfaces import IEntityOrder
from icemac.addressbook.interfaces import IKeywordTitles, ITitle, IPhoneNumber
from icemac.addressbook.interfaces import IPerson, IPersonDefaults, IEntity
from icemac.addressbook.interfaces import IPersonArchiving
from icemac.addressbook.interfaces import IPersonUnarchiving
from icemac.addressbook.interfaces import ISchemaName
from icemac.addressbook.person import Person, Keywords
import gocept.reference.interfaces
import gocept.reference.verify
import transaction
import zope.catalog.interfaces
import zope.component
import zope.dublincore.timeannotators
import zope.publisher.testing


def test_person__Person__1():
    """It fulfils the `IPerson` interface."""
    assert gocept.reference.verify.verifyObject(IPerson, Person())


def test_person__Person__2():
    """It fulfils the `IPersonDefaults` interface."""
    assert gocept.reference.verify.verifyObject(IPersonDefaults, Person())


def test_person__Person__3():
    """It fulfils the `IPersonArchiving` interface."""
    assert gocept.reference.verify.verifyObject(IPersonArchiving, Person())


def test_person__Person__4():
    """It fulfils the `IPersonUnarchiving` interface."""
    assert gocept.reference.verify.verifyObject(IPersonUnarchiving, Person())


def test_person__Person__schema__1(zcmlS):
    """It can be adapted to ``ISchemaName``."""
    assert 'IPerson' == ISchemaName(Person()).schema_name


def test_person__Keywords__1():
    """It fulfills the `IKeywordTitles` interface."""
    assert gocept.reference.verify.verifyObject(IKeywordTitles, Keywords(None))


def test_person__PersonDefaultsEntity__getRawFields__1(address_book):
    """It returns the fields in default sort order if no order is defined."""
    entity = IEntity(IPersonDefaults)
    assert ([
        'default_postal_address',
        'default_phone_number',
        'default_email_address',
        'default_home_page_address',
    ] == [x[0] for x in entity.getRawFields()])


def test_person__PersonDefaultsEntity__getRawFields__2(address_book):
    """It returns the fields in the entity sort order."""
    entity = IEntity(IPersonDefaults)
    zope.component.getUtility(IEntityOrder).up(IEntity(IPhoneNumber))
    assert ([
        'default_phone_number',
        'default_postal_address',
        'default_email_address',
        'default_home_page_address',
    ] == [x[0] for x in entity.getRawFields()])


def test_person__PersonDefaultsEntity__getRawFields__3(address_book):
    """It returns the fields in default order if called whih `sorted=False`."""
    entity = IEntity(IPersonDefaults)
    zope.component.getUtility(IEntityOrder).up(IEntity(IPhoneNumber))
    assert ([
        'default_postal_address',
        'default_phone_number',
        'default_email_address',
        'default_home_page_address',
    ] == [x[0] for x in entity.getRawFields(sorted=False)])


def test_person__Person__get_name__1():
    """It returns last name and first name if both are set."""
    person = Person()
    person.first_name = u'Bernd'
    person.last_name = u'Tester'
    assert u'Bernd Tester' == person.get_name()


def test_person__Person__get_name__2():
    """It returns the last name if the first name is not set."""
    person = Person()
    person.last_name = u'Tester'
    assert u'Tester' == person.get_name()


def test_person__Person__get_name__3():
    """It returns the first name if the last name is not set."""
    person = Person()
    person.first_name = u'Berns'
    assert u'Berns' == person.get_name()


def test_person__Person__get_name__4():
    """It returns '' if neither first name nor last name is set."""
    assert u'' == Person().get_name()


def test_person__Person__archive__1(
        address_book, FullPersonFactory, monkeypatch):
    """It moves the person to the archive and marks it as archived."""
    person = FullPersonFactory(address_book, u'tester')
    assert address_book == person.__parent__
    assert not IArchivedPerson.providedBy(person)
    rt = gocept.reference.interfaces.IReferenceTarget(person['PhoneNumber'])
    assert rt.is_referenced()
    now = zope.dublincore.timeannotators._now()
    monkeypatch.setattr(zope.dublincore.timeannotators, '_NOW', now)

    with zope.publisher.testing.interaction('principal_1'):
        person.archive()
        transaction.commit()
    assert address_book.archive == person.__parent__
    assert IArchivedPerson.providedBy(person)
    assert rt.is_referenced()
    assert now == person.archival_date
    assert 'principal_1' == person.archived_by


def test_person__Person__archive__2(address_book, FullPersonFactory):
    """It removes the person from the catalog."""
    person = FullPersonFactory(address_book, u'Older')
    catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
    assert 1 == len(catalog.searchResults(name='Older'))

    person.archive()
    assert 0 == len(catalog.searchResults(name='Older'))


def test_person__title__1(zcmlS):
    """The title of a person without a name is a fix string."""
    assert u'<no name>' == ITitle(Person())


def test_person__title__2(zcmlS):
    """`title()` returns the last name if the first name is empty."""
    person = Person()
    person.last_name = u'Tester'
    assert u'Tester' == ITitle(person)


def test_person__title__3(zcmlS):
    """`title()` returns the last name and first name comma separated."""
    person = Person()
    person.first_name = u'Hans'
    person.last_name = u'Tester'
    assert u'Tester, Hans' == ITitle(person)

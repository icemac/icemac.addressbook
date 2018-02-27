import zope.component
from icemac.addressbook.person import Person, Keywords
from icemac.addressbook.interfaces import IPerson, IPersonDefaults, IEntity
from icemac.addressbook.interfaces import IKeywordTitles, ITitle, IPhoneNumber
from icemac.addressbook.interfaces import IEntityOrder
from icemac.addressbook.interfaces import ISchemaName
import gocept.reference.verify


def test_person__Person__1():
    """It fulfills the `IPerson` interface."""
    assert gocept.reference.verify.verifyObject(IPerson, Person())


def test_person__Person__2():
    """It fulfills the `IPersonDefaults` interface."""
    assert gocept.reference.verify.verifyObject(IPersonDefaults, Person())


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

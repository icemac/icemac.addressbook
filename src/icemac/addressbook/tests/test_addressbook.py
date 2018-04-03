from icemac.addressbook.addressbook import AddressBook
from icemac.addressbook.addressbook import create_address_book_infrastructure
from icemac.addressbook.interfaces import IAddressBook, IKeywords, IEntities
from icemac.addressbook.interfaces import IArchive
from icemac.addressbook.interfaces import IOrderStorage, ENTITIES
import zope.authentication.interfaces
import zope.catalog.interfaces
import zope.component
import zope.interface.verify
import zope.intid.interfaces
import zope.location.interfaces
import zope.pluggableauth.interfaces


def test_addressbook__add_more_addressbook_infrastructure__1(
        address_book, PersonFactory):
    """`add_more_addressbook_infrastructure` installs an IntId utility."""
    # Persons added to the address book are added to the IntID utility of the
    # address book. (The int id changes with every run so we can only show,
    # that there is an int id registered for the person):
    person = PersonFactory(address_book, u'Kohn')
    intids = zope.component.getUtility(zope.intid.interfaces.IIntIds)
    assert None is not intids.queryId(person)
    assert isinstance(intids.queryId(person), int)
    assert person is intids.queryObject(intids.queryId(person))
    assert None is intids.queryId(object())


def test_addressbook__add_more_addressbook_infrastructure__2(
        address_book, PersonFactory):
    """`add_more_addressbook_infrastructure` creates an index for keywords."""
    # The keywords on persons are indexed.
    person = PersonFactory(
        address_book, u'Kohn', keywords=[u'church', u'friends'])
    # The index should now contain two words (the titles of the keywords.),
    # so we can search for them:
    catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
    assert 2 == catalog.get('keywords').wordCount.value
    results = catalog.searchResults(keywords={'any_of': ('friends', )})
    assert 1 == len(results)
    assert person is list(results)[0]


def test_addressbook__add_more_addressbook_infrastructure__3(
        address_book, PersonFactory):
    """`add_more_addressbook_infrastructure` creates an index for names."""
    # The first name and last name of the persons are indexed to be used in
    # quick search:
    person = PersonFactory(address_book, u'Kohn', first_name=u'Ernst')
    catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
    assert 1 == len(catalog.searchResults(name='K??n'))
    assert person is list(catalog.searchResults(name='K??n'))[0]
    assert 1 == len(catalog.searchResults(name='Erns*'))
    assert 0 == len(catalog.searchResults(name='Erns'))


def check_addressbook(assert_address_book):
    """Check the validity and completeness of the address book."""
    assert zope.location.interfaces.ISite.providedBy(
        assert_address_book.address_book)
    assert_address_book.has_attribute('keywords', IKeywords)
    assert_address_book.has_attribute(
        'principals', zope.pluggableauth.interfaces.IAuthenticatorPlugin,
        name=u'icemac.addressbook.principals')
    assert_address_book.has_attribute('entities', IEntities)
    assert_address_book.has_attribute('orders', IOrderStorage)
    assert_address_book.has_local_utility(zope.intid.interfaces.IIntIds)
    assert_address_book.has_local_utility(zope.catalog.interfaces.ICatalog)
    assert_address_book.has_local_utility(
        zope.authentication.interfaces.IAuthentication)


def test_addressbook__create_address_book_infrastructure__1(
        assert_address_book):
    """The address_book created within the fixture is valid."""
    check_addressbook(assert_address_book)


def test_addressbook__create_address_book_infrastructure__2(
        assert_address_book):
    """Calling `create_address_book_infrastructure` again does not break."""
    create_address_book_infrastructure(assert_address_book.address_book)
    check_addressbook(assert_address_book)


def test_addressbook__create_address_book_infrastructure__3(address_book):
    """`create_address_book_infrastructure` creates default entity order."""
    assert ([
        'IcemacAddressbookAddressbookAddressbook',
        'IcemacAddressbookPersonPerson',
        'IcemacAddressbookPersonPersondefaults',
        'IcemacAddressbookAddressPostaladdress',
        'IcemacAddressbookAddressPhonenumber',
        'IcemacAddressbookAddressEmailaddress',
        'IcemacAddressbookAddressHomepageaddress',
        'IcemacAddressbookFileFileFile',
        'IcemacAddressbookKeywordKeyword'] ==
        address_book.orders.byNamespace(ENTITIES))


def test_addressbook__create_address_book_infrastructure__4(address_book):
    """`create_address_book_infrastructure` creates only the entity order."""
    assert [ENTITIES] == list(address_book.orders.namespaces())


def test_addressbook__AddressBook__1(address_book):
    """`AddressBook` fulfills the `IAddressBook` interface."""
    zope.interface.verify.verifyObject(IAddressBook, address_book)


def test_addressbook__AddressBook____repr____1(address_book):
    """`__repr__()` renders name and title."""
    address_book.title = u'My address book'
    assert "<AddressBook u'ab' (u'My address book')>" == repr(address_book)


def test_addressbook__AddressBook____repr____2():
    """`__repr__()` does not break on missing name and title."""
    assert "<AddressBook None (None)>" == repr(AddressBook())


def test_addressbook__AddressBook____nonzero____1(address_book):
    """It is `True` even for an empty address book."""
    assert bool(address_book)


def test_addressbook__get_address_book__1(address_book):
    """Any object can be adated to IAddressBook to get the current one."""
    assert address_book == IAddressBook(42)
    assert address_book == IAddressBook(None)


def test_addressbook__Archive__1(address_book):
    """It fulfils the `IArchive` interface."""
    zope.interface.verify.verifyObject(IArchive, address_book.archive)


def test_addressbook__get_archive__1(address_book):
    """It returns the archive of the current address book."""
    assert address_book.archive == IArchive(None)

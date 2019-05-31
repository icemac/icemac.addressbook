# -*- coding: utf-8 -*-
from ..list import PersonList
from icemac.addressbook.fieldsource import tokenize
from icemac.addressbook.interfaces import IEMailAddress
from icemac.addressbook.interfaces import IHomePageAddress, IEntity
from icemac.addressbook.interfaces import IPerson, IPostalAddress, IPhoneNumber
from mock import Mock, patch, PropertyMock
import contextlib
import datetime
import gocept.country.db
import icemac.addressbook.testing
import pytest
import pytz
import transaction
import zope.component.hooks
import zope.interface


# ready to use fixtures

@pytest.yield_fixture(scope='function')
def MockPersons_22():
    """Create 22 mock persons.

    Also installs patches, so these mock persons can be rendered in PersonList.
    """
    with patch.object(PersonList, 'values',
                      new_callable=PropertyMock) as values, \
            patch('z3c.table.column.absoluteURL') as absoluteURL:
        values.return_value = [
            DummyPerson(
                first_name='first name {}'.format(x), last_name='last name')
            for x in range(22)]
        absoluteURL.return_value = 'http://url.to/person'
        yield


@pytest.yield_fixture(scope='function')
def some_persons(somePersonsS):
    """Some persons to test the sort order."""
    for connection in icemac.addressbook.conftest.pyTestStackDemoStorage(
            somePersonsS.zodb, 'some_persons'):
        yield


# Test helper functions


def assert_person_list(
        browser, result, columns, xpath='//td/text() | //td/a/text()', **kw):
    """Assert the contents of `PersonList` for a given set of columns."""
    prefs_mock = _get_prefs_mock(*columns, **kw)
    browser.login('visitor')
    with patch.object(PersonList, 'prefs',
                      new_callable=PropertyMock) as prefs:
        prefs.return_value = prefs_mock
        browser.open(browser.PERSONS_LIST_URL)
        assert result == browser.etree.xpath(xpath)


@contextlib.contextmanager
def batchSize(size):
    """Context manager to patch the user definable person list batch size."""
    with patch.object(PersonList, 'batchSize', new_callable=PropertyMock) as b:
        b.return_value = size
        yield


def _get_prefs_mock(*columns, **kw):
    """Get a mock for the preferences.

    columns ... show these columns in person lists
                has to be tuples (<entity interface>, <field name>)
    **kw might have the following keys:
        order_by ... order the columns in person lists by this tuple of
                     (<entity interface>, <field name>)
                     Default: (IPerson, 'last_name')
    """
    prefs_mock = Mock()
    prefs_mock.personListTab.batch_size = 20
    prefs_mock.personLists.sort_direction = 'ascending'
    prefs_mock.personLists.columns = [
        tokenize(IEntity(iface), field_name)
        for iface, field_name in columns]
    order_entitiy, order_field = kw.pop('order_by', (IPerson, 'last_name'))
    prefs_mock.personLists.order_by = tokenize(
        IEntity(order_entitiy), order_field)
    if 'sort_direction' in kw:
        prefs_mock.personLists.sort_direction = kw['sort_direction']
    return prefs_mock


# Infrastructure fixtures


@pytest.yield_fixture(scope='session')
def somePersonsS(addressBookS, FullPersonFactory):
    """Create some persons used in tests."""
    for connection in icemac.addressbook.conftest.pyTestStackDemoStorage(
            addressBookS, 'somePersonsS'):
        for address_book in icemac.addressbook.conftest.site(connection):
            FullPersonFactory(address_book, u'Tester', first_name=u'Hans',
                              birth_date=datetime.date(1975, 4, 2),
                              keywords=[u'church', u'Friends', u'family'])
            FullPersonFactory(address_book, u'Streber', first_name=u'Gunter',
                              keywords=[u'Friends'])
            FullPersonFactory(address_book, u'Utzer',
                              birth_date=datetime.date(1974, 5, 14))
            transaction.commit()
        yield connection


@zope.interface.implementer(IPerson)
class DummyPerson(object):
    """Light weight dummy IPerson object."""

    def __init__(self, **kw):
        self.__dict__.update(kw)


def test_list__PersonList__1(address_book, browser):
    """The person list is initially empty and shows a message."""
    browser.login('visitor')
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    browser.getLink('Person list').click()
    assert browser.PERSONS_LIST_URL == browser.url
    assert ('There are no persons entered yet, click on "Add person" to '
            'create one.' in browser.contents)


def test_list__PersonList__2(address_book, browser):
    """A user with the role `visitor` is not allowed to add new persons."""
    from zope.testbrowser.browser import LinkNotFoundError
    browser.login('visitor')
    browser.open(browser.PERSONS_LIST_URL)
    with pytest.raises(LinkNotFoundError):
        browser.getLink('person')


def test_list__PersonList__3(address_book, MockPersons_22, browser):
    """`PersonList` renders a pagination if number of persons > batch size."""
    browser.login('visitor')
    with batchSize(20):
        browser.open(browser.PERSONS_LIST_URL)
    assert ([
        ('1', '/person-list.html?table-batchSize=20&table-batchStart=0'),
        ('2', '/person-list.html?table-batchSize=20&table-batchStart=20')] ==
        [(x.text,
          x.attrib['href'].split(browser.ADDRESS_BOOK_DEFAULT_URL)[-1])
         for x in browser.etree.xpath('//div[@class="batch"]/a')])


def test_list__PersonList__4(address_book, MockPersons_22, browser):
    """`PersonList` renders no pagination if number of persons < batch size."""
    browser.login('visitor')
    with batchSize(23):
        browser.open(browser.PERSONS_LIST_URL)
    assert [] == browser.etree.xpath('//div[@class="batch"]/a')


def test_list__PersonList__5(address_book, MockPersons_22, browser):
    """`PersonList` renders a batch spacer if there are too many batches."""
    browser.login('visitor')
    with batchSize(1):
        browser.open(browser.PERSONS_LIST_URL)
    assert [u'…'] == [
        x.strip()
        for x in browser.etree.xpath('//div[@class="batch"]/text()')
        if x.strip()]


@pytest.mark.parametrize('batch_size, batch_number', ((19, 2), (8, 3)))
def test_list__PersonList__6i(
        address_book, MockPersons_22, browser, batch_size, batch_number):
    """`PersonList` respects the batch size set in the preferences."""
    browser.login('visitor')
    browser.open(browser.PREFS_URL)
    browser.getControl('batch size').value = str(batch_size)
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    browser.open(browser.PERSONS_LIST_URL)
    assert ([str(x + 1) for x in range(batch_number)] ==
            browser.etree.xpath('//div[@class="batch"]/a/text()'))


def test_list__PersonList__7i(
        address_book, FieldFactory, FullPersonFactory, browser):
    """`PersonList` renders user defined fields."""
    photo_permission = FieldFactory(
        address_book, IPerson, u'Bool', u'photo permission?').__name__
    last_seen = FieldFactory(
        address_book, IPerson, u'Datetime', u'last seen').__name__
    state = FieldFactory(
        address_book, IPostalAddress, u'Choice', u'state',
        values=[u'Sachsen', u'Sachsen-Anhalt', u'Brandenburg']).__name__
    number_of_letters = FieldFactory(
        address_book, IPostalAddress, u'Int', u'number of letters').__name__
    last_time_verified = FieldFactory(
        address_book, IPostalAddress, u'Date', u'last time verified').__name__
    cost_per_minute = FieldFactory(
        address_book, IPhoneNumber, u'Decimal', u'cost per minute').__name__
    mail_box_text = FieldFactory(
        address_book, IPhoneNumber, u'Text', u'mail box text').__name__
    company_home_page = FieldFactory(
        address_book, IHomePageAddress, u'URI', u'company home page').__name__
    home_page_provider = FieldFactory(
        address_book, IHomePageAddress, u'TextLine',
        u'home page provider').__name__

    # Using two persons here to show that user defined fields render
    # an empty value if not set.
    FullPersonFactory(
        address_book, u'Tester', **{
            'person__' + photo_permission: True,
            'postal__' + state: 'Brandenburg',
            'postal__' + number_of_letters: 42,
            'phone__' + cost_per_minute: 1.45,
            'phone__' + mail_box_text: 'Hi, I do not like the boring texts of '
                                       'the answering machines ...',
            'homepage__' + company_home_page: 'http://www.mycompany.de',
            'homepage__' + home_page_provider: 'mycomp',
        })
    FullPersonFactory(
        address_book, u'Utzer', **{
            'postal__' + last_time_verified: datetime.date(2001, 1, 8),
            'person__' + last_seen: datetime.datetime(
                2010, 9, 8, 20, 15, tzinfo=pytz.utc),
        })

    assert_person_list(
        browser,
        ['yes',
         '42',
         'Brandenburg',
         '1.45',
         u'Hi, I do not like the \u2026',
         'http://www.mycompany.de',
         'mycomp',
         'Tester',
         '2010 9 8  20:15:00 ',
         '2001 1 8 ',
         'Utzer'],
        ((IPerson, photo_permission),
         (IPerson, last_seen),
         (IPostalAddress, number_of_letters),
         (IPostalAddress, last_time_verified),
         (IPostalAddress, state),
         (IPhoneNumber, cost_per_minute),
         (IPhoneNumber, mail_box_text),
         (IHomePageAddress, company_home_page),
         (IHomePageAddress, home_page_provider),
         (IPerson, 'last_name')))


def test_list__PersonList__8i(
        address_book, FieldFactory, FullPersonFactory, browser, browser2):
    """`PersonList` omits deleted user defined field selected for display."""
    photo_permission = FieldFactory(
        address_book, IPerson, u'Bool', u'photo permission?').__name__
    FullPersonFactory(address_book, u'Tester', **{photo_permission: False})

    columns = ((IPerson, photo_permission),
               (IPerson, 'last_name'))

    # Column is displayed
    assert_person_list(browser, ['no', 'Tester'], columns)
    # Only a manager can delete the field:
    icemac.addressbook.testing.delete_field(browser2, photo_permission)
    # The delete column gets omitted from person list:
    browser.reload()
    assert_person_list(browser, ['Tester'], columns)


def test_list__PersonList__9i(
        address_book, FieldFactory, FullPersonFactory, browser, browser2):
    """`PersonList` doesn't break when the order-by field gets deleted."""
    photo_permission = FieldFactory(
        address_book, IPerson, u'Bool', u'photo permission?').__name__
    FullPersonFactory(address_book, u'Tester', **{photo_permission: False})
    columns = ((IPerson, photo_permission),
               (IPerson, 'last_name'))
    order_by = (IPerson, photo_permission)

    # Column is displayed
    assert_person_list(browser, ['no', 'Tester'], columns, order_by=order_by)
    # Only a manager can delete the field:
    icemac.addressbook.testing.delete_field(browser2, photo_permission)
    # The delete column gets omitted from person list:
    browser.reload()
    assert_person_list(browser, ['Tester'], columns, order_by=order_by)


def test_list__PersonList__10i(address_book, PersonFactory, browser):
    """`PersonList` respects the columns selected in the preferences."""
    PersonFactory(address_book, u'Tester', notes=u'my notes')
    browser.login('visitor')
    browser.open(browser.PREFS_URL)
    browser.getControl('columns').displayValue = [
        'person -- last name',
        'person -- notes',
    ]
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    browser.open(browser.PERSONS_LIST_URL)
    assert (['Tester', 'my notes'] ==
            browser.etree.xpath('//td/text() | //td/a/text()'))


def test_list__PersonList__11i(
        address_book, FullPersonFactory, EMailAddressFactory, browser):
    """`PersonList` renders all kinds of predefined fields."""
    # Using two persons here to show that the empty value is rendered
    # correctly, too.
    FullPersonFactory(
        address_book, u'Tester', **{
            'person__first_name': u'Hans',
            'person__notes': u'Gave him 20 Dollars in Jan 2010.',
            'person__birth_date': datetime.date(1977, 11, 24),
            'person__keywords': [u'Friend', u'church'],
            'postal__country': gocept.country.db.Country('JP'),
            'phone__number': u'110',
            'homepage__url': 'http://www.mycompany.de',
            'email__email': u'tester@example.com',
        })
    # Country with no value is not displayed.
    utzer = FullPersonFactory(
        address_book, u'Utzer', postal__country=None)
    # This e-mail address will not show up in the list as only the default ones
    # are displayed there:
    EMailAddressFactory(utzer, email=u'ben@utzer.org', set_as_default=False)

    assert_person_list(
        browser,
        ['Hans',
         'Tester',
         u'Gave him 20 Dollars in …',  # notes: truncated + ellipsed
         '1977 11 24 ',
         'church, Friend',  # keywords: comma separated + lower case sorted
         'Japan',
         '110',
         'http://www.mycompany.de',
         'tester@example.com',
         'Utzer'],
        ((IPerson, 'first_name'),
         (IPerson, 'last_name'),
         (IPerson, 'notes'),
         (IPerson, 'birth_date'),
         (IPerson, 'keywords'),
         (IPostalAddress, 'country'),
         (IPhoneNumber, 'number'),
         (IHomePageAddress, 'url'),
         (IEMailAddress, 'email')))


def test_list__PersonList__12i(address_book, FullPersonFactory, browser):
    """`PersonList` renders homepage addresses and emails as links."""
    FullPersonFactory(
        address_book, u'Tester', email__email=u'tester@example.com',
        homepage__url='http://tester.example.com')

    assert_person_list(
        browser,
        ['http://localhost/ab/Person',
         'mailto:tester@example.com',
         'http://tester.example.com'],
        ((IPerson, 'last_name'),
         (IEMailAddress, 'email'),
         (IHomePageAddress, 'url')), xpath='//td/a/@href')


def test_list__PersonList__13i(
        address_book, FullPersonFactory, EMailAddressFactory, browser):
    """`PersonList` respects changed default addresses."""
    tester = FullPersonFactory(
        address_book, u'Tester', email__email=u'1st@example.com')
    email = EMailAddressFactory(
        tester, email=u'2nd@example.com', set_as_default=False)

    assert_person_list(
        browser,
        ['Tester', '1st@example.com'],
        ((IPerson, 'last_name'), (IEMailAddress, 'email')))

    with zope.component.hooks.site(address_book):
        tester.default_email_address = email

    assert_person_list(
        browser,
        ['Tester', '2nd@example.com'],
        ((IPerson, 'last_name'), (IEMailAddress, 'email')))


def test_list__PersonList__14i(some_persons, browser):
    """`PersonList` can be sorted by person's first name."""
    assert_person_list(
        browser,
        ['Utzer', 'Streber', 'Gunter', 'Tester', 'Hans'],
        [(IPerson, 'last_name'),
         (IPerson, 'first_name')],
        order_by=(IPerson, 'first_name'))


def test_list__PersonList__15i(some_persons, browser):
    """`PersonList` sorts by 1st column if order_by col is not displayed.

    Empty values in a column are sorted to the end of the column.
    """
    assert_person_list(
        browser,
        ['1974 5 14 ', 'Utzer', '1975 4 2 ', 'Tester', 'Streber'],
        [(IPerson, 'birth_date'),
         (IPerson, 'last_name')],
        order_by=(IPostalAddress, 'city'))


def test_list__PersonList__16i(some_persons, browser):
    """`PersonList` sorts keyword column by lower case of the cell contents."""
    assert_person_list(
        browser,
        ['Utzer', 'Tester', 'church, family, Friends', 'Streber', 'Friends'],
        [(IPerson, 'last_name'),
         (IPerson, 'keywords')],
        order_by=(IPerson, 'keywords'))


def test_list__PersonList__17i(some_persons, browser):
    """`PersonList` sorts keyword column by lower case of the cell contents."""
    assert_person_list(
        browser,
        ['Utzer', 'Tester', 'church, family, Friends', 'Streber', 'Friends'],
        [(IPerson, 'last_name'),
         (IPerson, 'keywords')],
        order_by=(IPerson, 'keywords'))


def test_list__PersonList__18i(some_persons, browser):
    """`PersonList` allows the user to change the sort order."""
    xpath = '//td/a/text()'
    assert_person_list(
        browser,
        ['Streber', 'Gunter', 'Tester', 'Hans', 'Utzer'],
        [(IPerson, 'last_name'),
         (IPerson, 'first_name')],
        order_by=(IPerson, 'last_name'),
        xpath=xpath)
    browser.getLink('first name').click()
    assert ('http://localhost/ab/@@person-list.html?'
            'table-sortOn=table-first_name-1&table-sortOrder=ascending' ==
            browser.url)
    assert (['Utzer', 'Streber', 'Gunter', 'Tester', 'Hans'] ==
            browser.etree.xpath(xpath))


def test_list__PersonList__19i(some_persons, browser):
    """`PersonList` uses sort direction defined in prefs.

    It additionally allows the user to change the sort direction using a link.
    """
    xpath = '//td/a/text()'
    assert_person_list(
        browser,
        ['Utzer', 'Tester', 'Hans', 'Streber', 'Gunter'],
        [(IPerson, 'last_name'),
         (IPerson, 'first_name')],
        order_by=(IPerson, 'last_name'),
        sort_direction='descending',
        xpath=xpath)
    browser.getLink('last name').click()
    assert ('http://localhost/ab/@@person-list.html?'
            'table-sortOn=table-last_name-0&table-sortOrder=ascending' ==
            browser.url)
    assert (['Streber', 'Gunter', 'Tester', 'Hans', 'Utzer'] ==
            browser.etree.xpath(xpath))


def test_list__PersonList__20(address_book, browser):
    """It cannot be accessed by an archivist user."""
    browser.login('archivist')
    browser.assert_forbidden(browser.PERSONS_LIST_URL)

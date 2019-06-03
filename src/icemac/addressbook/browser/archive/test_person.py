from __future__ import unicode_literals
from icemac.addressbook.interfaces import IPerson
from icemac.addressbook.interfaces import IPhoneNumber
from zope.testbrowser.browser import LinkNotFoundError
import gocept.country.db
import icemac.addressbook.interfaces
import lxml.html
import pytest


@pytest.fixture('function')
def archived_person(
        address_book, FullPersonFactory, KeywordFactory, FileFactory):
    """Create an archived person."""
    person = FullPersonFactory(
        address_book, 'Vregga', first_name='V.',
        keywords=set([KeywordFactory(address_book, 'friend')]))
    FileFactory(person, 'cv.txt', data='boring text', mimeType=b'text/plain')
    person.archive()
    yield person


def test_person__ArchivedPersonForm__1(address_book, PersonFactory, browser):
    """It can be accessed from the archive listing view."""
    person = PersonFactory(address_book, 'Vregga')
    person.archive()

    browser.login('archivist')
    browser.open(browser.ARCHIVE_URL)
    browser.getLink('Vregga').click()
    assert browser.ARCHIVE_PERSON_URL == browser.url


def test_person__ArchivedPersonForm__2(
        address_book, FullPersonFactory, FieldFactory, PhoneNumberFactory,
        browser):
    """It can be accessed from the archive listing view."""
    bool_field = FieldFactory(
        address_book, IPerson, 'Bool', 'alive?').__name__
    select_field = FieldFactory(
        address_book, IPhoneNumber, 'Choice', 'kind',
        values=['private', 'work number']).__name__

    person = FullPersonFactory(
        address_book, u'Tester', first_name=u'Petra',
        keywords=[u'family', u'church'],
        postal__address_prefix=u'c/o Mama', postal__zip=u'88888',
        postal__street=u'Demoweg 23', postal__city=u'Testhausen',
        postal__country=gocept.country.db.Country('AT'),
        phone__number=u'+4901767654321', email__email=u'petra@example.com',
        homepage__url=b'http://petra.example.com',
        **{bool_field: True})

    PhoneNumberFactory(
        person, **{
            'number': u'02225 88 82 33',
            select_field: 'work number'})

    person.archive()

    field = icemac.addressbook.interfaces.IPerson['first_name']
    customization = icemac.addressbook.interfaces.IFieldCustomization(
        address_book)
    customization.set_value(field, u'label', u'Christian Name')
    customization.set_value(field, u'description', u'given at baptism')

    browser.login('archivist')
    browser.open(browser.ARCHIVE_PERSON_URL)
    raw_text = lxml.html.document_fromstring(browser.contents).text_content()
    assert 'church, family' in raw_text
    assert '>yes<' in browser.contents
    assert 'Austria' in browser.contents
    assert 'work number' in browser.contents
    # Metadata is rendered:
    assert '>Creation Date (UTC)<' in browser.contents
    # Field customizations are rendered:
    assert 'Christian Name' in browser.contents
    assert 'given at baptism' in browser.contents


@pytest.mark.parametrize('loginname', [
    'archivist',
    'mgr',
])
def test_person__ArchivedPersonForm__3(archived_person, browser, loginname):
    """It renders a read-only form of person's data for all allowed users.

    There are no add links but an unarchive button.
    """
    browser.login(loginname)
    browser.open(browser.ARCHIVE_PERSON_URL)
    assert [
        'form.buttons.unarchive',
    ] == browser.all_control_names

    assert '>Add<' not in browser.contents
    with pytest.raises(LinkNotFoundError):
        browser.getLink('postal address')


def test_person__ArchivedPersonForm__4(archived_person, browser):
    """It renders a read-only form for 'archive-visitor' without an unarchive

    form.
    """
    browser.login('archive-visitor')
    browser.open(browser.ARCHIVE_PERSON_URL)
    assert [] == browser._getAllResponseForms()


@pytest.mark.parametrize('loginname', ['editor', 'visitor'])
def test_person__ArchivedPersonForm__5(
        address_book, PersonFactory, browser, loginname):
    """It can only be accessed by allowed users."""
    person = PersonFactory(address_book, 'Vregga')
    person.archive()

    browser.login(loginname)
    browser.assert_forbidden(browser.ARCHIVE_PERSON_URL)


def test_person__UnarchivePersonForm__1(archived_person, browser, browser2):
    """It allows to unarchive an archived person after confirmation."""
    browser.login('archivist')
    browser.open(browser.ARCHIVE_PERSON_URL)
    browser.getControl('Unarchive person').click()
    assert browser.UNARCHIVE_PERSON_CONFIRM_URL == browser.url
    browser.getControl('Yes, unarchive').click()
    assert browser.ARCHIVE_URL == browser.url
    assert '"Vregga, V." unarchived.' == browser.message
    browser.open(browser.ARCHIVE_URL)  # get rid of message
    assert 'Vregga' not in browser.contents
    del browser

    # The person can be edited again:
    browser2.login('editor')
    browser2.open(browser2.PERSON_EDIT_URL)
    assert browser2.getControl('first name').value == 'V.'
    browser2.getControl('first name').value = 'Victor'
    browser2.getControl('Save').click()
    assert 'Data successfully updated.' == browser2.message

    # can be found in search:
    browser2.open(browser2.SEARCH_BY_NAME_URL)
    browser2.open(browser2.SEARCH_BY_NAME_URL)
    browser2.getControl('Name').value = 'Vregga'
    browser2.getControl('Search').click()
    assert browser2.getLink('Vregga').url.startswith(browser2.PERSON_EDIT_URL)


def test_person__UnarchivePersonForm__2(archived_person, browser):
    """It allows to cancel unarchiving an archived person."""
    browser.login('archivist')
    browser.open(browser.UNARCHIVE_PERSON_CONFIRM_URL)
    browser.getControl('No, cancel').click()
    assert browser.ARCHIVE_PERSON_URL == browser.url
    assert 'Unarchiving canceled.' == browser.message
    assert [
        'form.buttons.unarchive',
    ] == browser.all_control_names


@pytest.mark.parametrize('loginname', ['editor', 'visitor', 'archive-visitor'])
def test_person__UnarchivePersonForm__3(archived_person, browser, loginname):
    """It cannot be accessed by several "lower" roles."""
    browser.login(loginname)
    browser.assert_forbidden(browser.UNARCHIVE_PERSON_CONFIRM_URL)

from __future__ import unicode_literals
from icemac.addressbook.interfaces import IPerson
from icemac.addressbook.interfaces import IPhoneNumber
from zope.testbrowser.browser import LinkNotFoundError
import gocept.country.db
import lxml.html
import pytest


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

    browser.login('archivist')
    browser.open(browser.ARCHIVE_PERSON_URL)
    raw_text = lxml.html.document_fromstring(browser.contents).text_content()
    assert 'family, church' in raw_text
    assert '>yes<' in browser.contents
    assert 'Austria' in browser.contents
    assert 'work number' in browser.contents


@pytest.mark.parametrize('loginname', [
    'archivist',
    'archive-visitor',
    'mgr',
])
def test_person__ArchivedPersonForm__3(
        address_book, FullPersonFactory, KeywordFactory, FileFactory, browser,
        loginname):
    """It renders a read-only form of person's data for all allowed users.

    There are no add links.
    """
    person = FullPersonFactory(
        address_book, 'Vregga', first_name='V.',
        keywords=set([KeywordFactory(address_book, 'friend')]))
    FileFactory(person, 'cv.txt', data='boring text', mimeType=b'text/plain')
    person.archive()

    browser.login(loginname)
    browser.open(browser.ARCHIVE_PERSON_URL)
    assert [
        'form.buttons.unarchive',
    ] == browser.all_control_names

    assert '>Add<' not in browser.contents
    with pytest.raises(LinkNotFoundError):
        browser.getLink('postal address')


@pytest.mark.parametrize('loginname', ['editor', 'visitor'])
def test_person__ArchivedPersonForm__4(
        address_book, PersonFactory, browser, loginname):
    """It can only be accessed by allowed users."""
    person = PersonFactory(address_book, 'Vregga')
    person.archive()

    browser.login(loginname)
    browser.assert_forbidden(browser.ARCHIVE_PERSON_URL)

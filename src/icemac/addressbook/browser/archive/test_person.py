from __future__ import unicode_literals
import pytest


def test_person__ArchivedPersonForm__1(address_book, PersonFactory, browser):
    """It can be accessed from the archive listing view."""
    person = PersonFactory(address_book, 'Vregga')
    person.archive()

    browser.login('archivist')
    browser.open(browser.ARCHIVE_URL)
    browser.getLink('Vregga').click()
    assert browser.ARCHIVE_PERSON_URL == browser.url


@pytest.mark.parametrize('loginname', [
    'archivist',
    'mgr',
    'editor_and_archivist',
])
def test_person__ArchivedPersonForm__2(
        address_book, FullPersonFactory, KeywordFactory, browser, loginname):
    """It renders a read-only form of person's data for all allowed users."""
    person = FullPersonFactory(
        address_book, 'Vregga', first_name='V.',
        keywords=set([KeywordFactory(address_book, 'friend')]))
    person.archive()

    browser.login(loginname)
    browser.open(browser.ARCHIVE_PERSON_URL)
    assert [
        'form.buttons.apply',
        'form.buttons.cancel',
        'form.buttons.export',
    ] == browser.all_control_names

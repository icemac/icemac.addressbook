from .interfaces import IEditor
from datetime import datetime
from zope.dublincore.interfaces import IZopeDublinCore
import icemac.addressbook.metadata.storage
import pytest
import zope.interface.verify


@pytest.yield_fixture(scope='function')
def person(address_book, browser):
    """Create a person using a browser so `creator` is set."""
    browser.login('editor')
    browser.open(browser.PERSON_ADD_URL)
    browser.getControl('last name').value = 'Tester'
    browser.getControl('Add').click()
    assert '"Tester" added.' == browser.message
    # Set address_book as site again as using a browser resets it.
    with zope.component.hooks.site(address_book):
        yield address_book['Person']


def test_storage__EditorMetadataStorage__1():
    """`EditorMetadataStorage` conforms to `IEditor`."""
    assert zope.interface.verify.verifyObject(
        IEditor,
        icemac.addressbook.metadata.storage.EditorMetadataStorage())


def test_subscriber__1(address_book, PersonFactory):
    """Zope sets the creation date on creation."""
    person = PersonFactory(address_book, u'Tester')
    assert isinstance(IZopeDublinCore(person).created, datetime)


def test_subscriber__CreatorAnnotator__1(person):
    """`CreatorAnnotator` sets the creator on adding a person with browser."""
    assert u'global editor' == IEditor(person).creator


def test_subscriber__LastModifierAnnotator__1(person):
    """`LastModifierAnnotator` sets creator as last modifier at creation."""
    assert u'global editor' == IEditor(person).modifier


def test_subscriber__LastModifierAnnotator__2(
        address_book, person, UserFactory, browser2):
    """`LastModifierAnnotator` sets last modifier at modification."""
    # Users inside the address book are valid modifiers, too.
    UserFactory(address_book, u'Hans', u'Tester', u'hans@test.de',
                u'12345678', ['Editor'])
    browser = browser2.formlogin('hans@test.de', '12345678')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getControl('notes').value = 'I was here.'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    assert u'global editor' == IEditor(person).creator
    assert u'Tester, Hans' == IEditor(person).modifier

from icemac.addressbook.browser.entities.fields import get_field_customization
from icemac.addressbook.interfaces import IPerson, IEntity
from zope.testbrowser.browser import LinkNotFoundError
import icemac.addressbook.interfaces
import icemac.addressbook.metadata.interfaces
import pytest
import zope.component.hooks
import zope.dublincore.interfaces


@pytest.mark.parametrize('username', ('editor', 'visitor'))
def test_fields__security__1(address_book, browser, username):
    """A user with a non-admin role has no edit link at master data."""
    browser.login(username)
    browser.open(browser.MASTER_DATA_URL)
    with pytest.raises(LinkNotFoundError):
        browser.getLink('Entities')


@pytest.mark.parametrize('username', ('editor', 'visitor'))
def test_fields__security__2(address_book, browser, username):
    """A user with a non-admin role cannot access the view to edit entities."""
    browser.login(username)
    browser.assert_forbidden(browser.ENTITIES_EDIT_URL)


@pytest.mark.parametrize('username', ('editor', 'visitor'))
def test_fields__security__3(address_book, browser, username):
    """A non-admin cannot access the view to edit fields of an entity."""
    browser.login(username)
    browser.assert_forbidden(browser.ENTITY_PERSON_LIST_FIELDS_URL)


@pytest.mark.parametrize('username', ('editor', 'visitor'))
def test_fields__security__4(address_book, browser, username):
    """A non-admin cannot add a new user defined field."""
    browser.login(username)
    browser.assert_forbidden(browser.ENTITY_PERSON_ADD_FIELD_URL)


@pytest.mark.parametrize('username', ('editor', 'visitor'))
def test_fields__security__5(address_book, FieldFactory, browser, username):
    """A a non-admin cannot edit a user defined field."""
    FieldFactory(address_book, IPerson, 'TextLine', u'baz')
    browser.login(username)
    browser.assert_forbidden(browser.ENTITIY_PERSON_EDIT_FIELD_URL)


@pytest.mark.parametrize('username', ('editor', 'visitor'))
def test_fields__security__6(address_book, FieldFactory, browser, username):
    """A a non-admin cannot delete a user defined field."""
    FieldFactory(address_book, IPerson, 'TextLine', u'baz')
    browser.login(username)
    browser.assert_forbidden(browser.ENTITIY_PERSON_DELETE_FIELD_URL)


def test_fields__List__fields__1(address_book, browser):
    """It omits fields which are tagged with `omit-from-field-list`."""
    browser.login('mgr')
    browser.open(browser.ENTITY_PERSON_LIST_FIELDS_URL)
    # Initially the field is displayed:
    assert 'birth date' in browser.contents
    try:
        IPerson['birth_date'].setTaggedValue('omit-from-field-list', True)
        browser.open(browser.ENTITY_PERSON_LIST_FIELDS_URL)
        # It is not displayed after setting `omit-from-field-list`:
        assert 'birth date' not in browser.contents
    finally:
        IPerson['birth_date'].setTaggedValue('omit-from-field-list', False)


def test_fields__AddForm__1(address_book, browser):
    """New fields can be added to entities.

    The user has to select an entity first and then choose the `add field`
    link:

    """
    browser.login('mgr')
    browser.open(browser.MASTER_DATA_URL)
    browser.getLink('Entities').click()
    assert browser.ENTITIES_EDIT_URL == browser.url
    browser.getLink('Edit fields', index=1).click()
    assert browser.ENTITY_PERSON_LIST_FIELDS_URL == browser.url
    browser.getLink('field').click()
    assert browser.ENTITY_PERSON_ADD_FIELD_URL == browser.url
    # When all invariants are satisfied, the form gets saved:
    browser.getControl('type').displayValue = ['text line']
    browser.getControl('title').value = 'baz'
    browser.getControl('notes').value = 'the baz field'
    browser.getControl(name='form.buttons.add').click()
    assert '"baz" added.' == browser.message
    assert browser.ENTITY_PERSON_LIST_FIELDS_URL == browser.url
    assert browser.ENTITIY_PERSON_DELETE_FIELD_URL in browser.contents


def test_fields__AddForm__2(address_book, browser):
    """Selecting the `choice` type requires values."""
    browser.login('mgr')
    browser.open(browser.ENTITY_PERSON_ADD_FIELD_URL)
    browser.getControl('type').displayValue = ['choice']
    browser.getControl('title').value = 'foobar'
    browser.getControl(name='form.buttons.add').click()
    assert [] == browser.message
    assert browser.ENTITY_PERSON_ADD_FIELD_URL == browser.url
    assert (
        '<div class="error">type "choice" requires at least one field value.'
        in browser.contents)


def test_fields__AddForm__3(address_book, FieldFactory, browser):
    """The ids of previously deleted fields are not reused."""
    FieldFactory(address_book, IPerson, 'TextLine', u'baz')
    browser.login('mgr')
    browser.open(browser.ENTITIY_PERSON_DELETE_FIELD_URL)
    browser.getControl('Yes').click()
    assert '"baz" deleted.' == browser.message

    browser.open(browser.ENTITY_PERSON_ADD_FIELD_URL)
    browser.getControl('type').displayValue = ['text line']
    browser.getControl('title').value = 'baz'
    browser.getControl(name='form.buttons.add').click()
    assert '"baz" added.' == browser.message
    assert browser.ENTITY_PERSON_LIST_FIELDS_URL == browser.url
    assert browser.getLink('Edit', index=5).url.endswith(
        '/icemac.addressbook.person.Person/Field-2')
    assert browser.ENTITIY_PERSON_EDIT_FIELD_URL != browser.getLink('Edit').url


def test_fields__EditForm__1(address_book, FieldFactory, browser):
    """When editing a user defined field the values are displayed.

    Values can be changed.
    """
    FieldFactory(
        address_book, IPerson, 'TextLine', u'baz', notes=u'the baz field')
    browser.login('mgr')
    browser.open(browser.ENTITY_PERSON_LIST_FIELDS_URL)
    browser.getLink('Edit', index=5).click()
    assert browser.ENTITIY_PERSON_EDIT_FIELD_URL == browser.url
    assert ['text line'] == browser.getControl('type').displayValue
    assert 'baz' == browser.getControl('title').value
    assert 'the baz field' == browser.getControl('notes').value

    browser.getControl('title').value = 'foobar'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.ENTITY_PERSON_LIST_FIELDS_URL == browser.url
    browser.getLink('Edit', index=5).click()
    assert browser.ENTITIY_PERSON_EDIT_FIELD_URL == browser.url
    assert 'foobar' == browser.getControl('title').value


def test_fields__EditForm__2(address_book, FieldFactory, browser):
    """When canceling the edit of a field the previous values are kept."""
    FieldFactory(address_book, IPerson, 'TextLine', u'foo')
    browser.login('mgr')
    browser.open(browser.ENTITIY_PERSON_EDIT_FIELD_URL)
    browser.getControl('title').value = 'barrrrrrr'
    browser.getControl('Cancel').click()
    assert 'No changes were applied.' == browser.message
    browser.getLink('Edit', index=5).click()
    assert browser.ENTITIY_PERSON_EDIT_FIELD_URL == browser.url
    assert 'foo' == browser.getControl('title').value


def test_fields__DeleteForm__1(address_book, FieldFactory, browser):
    """An `administrator` can delete a user defined field."""
    FieldFactory(address_book, IPerson, 'TextLine', u'foobar')
    browser.login('mgr')
    browser.open(browser.ENTITY_PERSON_LIST_FIELDS_URL)
    assert 'foobar' in browser.contents
    browser.getLink('Delete').click()
    assert browser.ENTITIY_PERSON_DELETE_FIELD_URL == browser.url
    browser.getControl('Yes').click()
    assert '"foobar" deleted.' == browser.message
    assert browser.ENTITY_PERSON_LIST_FIELDS_URL == browser.url
    assert 1 == browser.contents.count('foobar')  # the one from the message


def test_fields__DeleteForm__2(address_book, FieldFactory, browser):
    """`Administrator` can choose to cancel deleting a user defined field."""
    FieldFactory(address_book, IPerson, 'TextLine', u'foobar')
    browser.login('mgr')
    browser.open(browser.ENTITIY_PERSON_DELETE_FIELD_URL)
    browser.getControl('No, cancel').click()
    assert 'Deletion canceled.' == browser.message
    assert browser.ENTITY_PERSON_LIST_FIELDS_URL == browser.url


def test_fields__SaveSortorder__1(address_book, FieldFactory, browser):
    """The sort order of the fields of the entities can be changed globally.

    To show that the sort order includes user defined fields.
    The places where fields are displayed in order are changed accordingly.

    """
    FieldFactory(address_book, IPerson, 'Bool', u'grown-up')
    # There is no field order saved yet:
    assert [] == IEntity(IPerson).getFieldOrder()
    browser.login('mgr')
    # The sort order is changed using JavaScript (tested using Selenium). When
    # the user hits the `Save sortorder` button a URL is generated and sent to
    # the server:
    browser.open(browser.ENTITY_PERSON_LIST_FIELDS_URL +
                 '/@@save-sortorder.html?f:list=last_name&f:list=Field-1')
    assert 'Saved sortorder.' == browser.message
    with zope.component.hooks.site(address_book):
        assert [u'last_name', u'Field-1'] == IEntity(IPerson).getFieldOrder()


def test_fields__RenameForm__1(address_book, FullPersonFactory, browser):
    """It enables renaming of a pre-defined field."""
    FullPersonFactory(address_book, u'Tester', first_name=u'Ben')

    browser.login('mgr')
    browser.open(browser.ENTITY_PERSON_LIST_FIELDS_URL)
    browser.getLink('Edit').click()
    assert browser.ENTITIY_PERSON_RENAME_FIELD_URL == browser.url
    assert 'first name' == browser.getControl('title').value
    browser.getControl('title').value = 'given name'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.ENTITY_PERSON_LIST_FIELDS_URL == browser.url
    browser.getLink('Edit').click()
    assert 'given name' == browser.getControl('title').value

    browser.open(browser.PERSON_EDIT_URL)
    assert 'Ben' == browser.getControl('given name').value


def test_fields__RenameForm__2(translated_address_book, browser):
    """It translates the default title."""
    browser.lang('de')
    browser.login('mgr')
    browser.open(browser.ENTITIY_PERSON_RENAME_FIELD_URL)
    assert 'Vorname' == browser.getControl('Bezeichnung').value


class DummyAttrib(object):
    """Dummy WidgetAttribute."""


def test_fields__get_field_customization__1(address_book, PersonFactory):
    """It returns the application customized title of a field, if

    there is no user customization.
    """
    person = PersonFactory(address_book, u'Vukasinovitch')
    attr = DummyAttrib()
    attr.context = person
    attr.field = zope.dublincore.interfaces.IDCTimes['created']
    custom_value = get_field_customization('label')
    with zope.publisher.testing.interaction('principal_1'):
        assert u'Creation Date (${timezone})' == custom_value(attr)


def test_fields__get_field_customization__2(address_book, PersonFactory):
    """It returns the user customized title of a field, if

    there is a user customization.
    """
    person = PersonFactory(address_book, u'Vukasinovitch')
    attr = DummyAttrib()
    attr.context = person
    attr.field = zope.dublincore.interfaces.IDCTimes['created']

    customization = icemac.addressbook.interfaces.IFieldCustomization(
        address_book)
    customization.set_label(attr.field, u'Custom Creation Date Label')

    custom_value = get_field_customization('label')
    with zope.publisher.testing.interaction('principal_1'):
        assert u'Custom Creation Date Label' == custom_value(attr)


def test_fields__get_field_customization__3(address_book, PersonFactory):
    """It returns the framework default title of a field, if

    there is no customization at all.
    """
    person = PersonFactory(address_book, u'Vukasinovitch')
    attr = DummyAttrib()
    attr.context = person
    attr.field = icemac.addressbook.metadata.interfaces.IEditor['creator']

    custom_value = get_field_customization('label')
    with zope.publisher.testing.interaction('principal_1'):
        assert u'creator' == custom_value(attr)

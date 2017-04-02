# -*- coding: utf-8 -*-
from icemac.addressbook.interfaces import IKeyword
from icemac.addressbook.testing import WebdriverPageObjectBase, Webdriver
import pytest


class POEntities(WebdriverPageObjectBase):
    """Webdriver page object for the entities page."""

    paths = [
        'ENTITY_PERSON_LIST_FIELDS_URL',
    ]

    _ENTITY_SELECTOR = "//tr[{}]/td[1]"

    def get_pos(self, pos):
        return self._selenium.getText(self._ENTITY_SELECTOR.format(pos))

    def move_to(self, pos, target):
        self._selenium.dragAndDropToObject(
            self._ENTITY_SELECTOR.format(pos),
            self._ENTITY_SELECTOR.format(target))

    def save(self):
        self._selenium.click("entity-fields-save")


Webdriver.attach(POEntities, 'entities')


@pytest.mark.webdriver
@pytest.mark.flaky(reruns=3)
def test_FieldOrder__1_webdriver(address_book, webdriver):
    """The fields of the entity can be sorted."""
    entities = webdriver.entities
    webdriver.login('mgr', entities.ENTITY_PERSON_LIST_FIELDS_URL)
    assert 'first name' == entities.get_pos(1)
    assert 'keywords' == entities.get_pos(4)
    entities.move_to(4, 1)
    # After saving the field is still on the first position:
    entities.save()
    assert 'Saved sortorder.' == webdriver.message
    assert 'keywords' == entities.get_pos(1)


def test_FieldOrder__2(address_book, browser):
    """Displaying the entity it shows the meta data of the entity field order.

    Because entities itself are not persistent.

    """
    browser.login('mgr')
    browser.open(
        browser.ENTITIES_EDIT_URL +
        '/icemac.addressbook.address.PostalAddress/@@save-sortorder.html?'
        'f:list=country&f:list=address_prefix&f:list=street&f:list=city&'
        'f:list=zip')
    assert ('<span id="form-widgets-creator" '
            'class="text-widget textline-field">Manager' in browser.contents)


def test_Entities__1(address_book, UserFactory, browser):
    """A local administrator is able to edit the entities."""
    UserFactory(address_book, u'Ad', u'Min', u'ad@min.de', u'12345678',
                ['Administrator'])
    # Log in as the local administrator and navigate to the edit entities
    # section of the master data:
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    browser.getControl('User Name').value = 'ad@min.de'
    browser.getControl('Password').value = '12345678'
    browser.getControl('Log in').click()
    assert 'You have been logged-in successfully.' == browser.message
    browser.getLink('Master data').click()
    browser.getLink('Entities').click()
    assert browser.ENTITIES_EDIT_URL == browser.url
    assert '<td>address book</td>' in browser.contents
    assert '<td>person</td>' in browser.contents


def test_Fields__1(address_book, browser):
    """Choice field values can contain non-ASCII characters."""
    # Create a user defined choice field and a values containing a non-ASCII
    # character:
    browser.login('mgr')
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    browser.getLink('Master data').click()
    browser.getLink('Entities').click()
    browser.getLink('Edit fields', index=1).click()
    assert browser.url.endswith(
        '++attribute++entities/icemac.addressbook.person.Person')
    browser.getLink('field').click()
    browser.getControl('type').displayValue = ['choice']
    browser.getControl('title').value = 'Ümläuttößt'
    browser.getControl('Add', index=0).click()
    assert [] == browser.message
    browser.getControl('value').value = 'Küche'
    browser.getControl('Add', index=1).click()
    assert u'"\xdcml\xe4utt\xf6\xdft" added.' == browser.message
    assert browser.url.endswith(
        '++attribute++entities/icemac.addressbook.person.Person')

    # Previously an error occurred when adding a new object for the entity with
    # the user defined field (a person in our case):
    browser.getLink('Person list').click()
    browser.getLink('person').click()
    assert ['No value', 'K\xc3\xbcche'] == browser.getControl(
        'Ümläuttößt').displayOptions


def test_Fields__2(address_book, FieldFactory, KeywordFactory, browser):
    """Deleting a value of a user defined choice field does not break the UI.

    Scenario: A user defined field is a choice. One of the values of this
    choice was chosen by a user. The administrator deletes this value in
    the choice. The form where the no longer existing choice value would
    be displayed does not break.

    """
    field_name = FieldFactory(address_book, IKeyword, 'Choice', u'kind',
                              values=[u'one', u'two', u'three']).__name__
    KeywordFactory(address_book, u'foo', **{field_name: u'two'})
    browser.login('mgr')
    browser.open(browser.KEYWORDS_LIST_URL)
    # Editing is possible, the entered values are stored:
    browser.getLink('foo').click()
    assert 'foo' == browser.getControl('keyword').value
    assert ['two'] == browser.getControl('kind').displayValue
    # When the selected value of the choice gets deleted, ...
    browser.getLink('Master data').click()
    browser.getLink('Entities').click()
    browser.getLink('Edit fields', index=7).click()
    assert browser.url.endswith(
        '++attribute++entities/icemac.addressbook.keyword.Keyword')
    browser.getLink('Edit').click()
    assert browser.url.endswith(
        '++attribute++entities/icemac.addressbook.keyword.Keyword/Field-1')
    remove = browser.getControl(name='form.widgets.values.1.remove')
    remove.getControl(value='1').click()
    browser.getControl(name='form.widgets.values.buttons.remove').click()
    browser.getControl('Apply').click()
    assert 'Data successfully updated.' == browser.message
    # the value is no longer displayed for the keyword:
    browser.getLink('Master data').click()
    browser.getLink('Keywords').click()
    browser.getLink('foo').click()
    assert ['No value', 'one', 'three'] == browser.getControl(
        'kind').displayOptions
    assert ['No value'] == browser.getControl('kind').displayValue

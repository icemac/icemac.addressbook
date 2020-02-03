# -*- coding: utf-8 -*-
from icemac.addressbook.file.interfaces import IFile
from icemac.addressbook.interfaces import IEntityOrder, IEntity
from icemac.addressbook.interfaces import IPerson, IPostalAddress
from icemac.addressbook.testing import set_modified, delete_field
from zope.dublincore.interfaces import IZopeDublinCore
import gocept.country.db
import pytest
import zope.component.hooks
import zope.testbrowser.interfaces


def form_fields_names(browser):
    """Get a list of field names as "<entity name>.<field name>"."""
    fields = ['.'.join(x.replace('IcemacAddressbookPerson', '')
                       .replace('IcemacAddressbookAddress', '')
                       for x in x.name.split('.')[-2:])
              for x in browser.getForm().controls
              if not zope.testbrowser.interfaces.IItemControl.providedBy(x)]
    # Omit empty marker hidden fields as they are too technical:
    return [x for x in fields if not x.endswith('-empty-marker')]


def test_person__PersonAddForm__1(address_book, browser):
    """`PersonAddForm` allows editors to add new persons."""
    browser.login('editor')
    browser.open(browser.PERSONS_LIST_URL)
    browser.getLink('person').click()
    assert browser.PERSON_ADD_URL == browser.url
    # There are fields for the person's personal data:
    browser.getControl('first name').value = u'Hans'
    browser.getControl('last name').value = u'Tester'
    browser.getControl('birth date').value = u'2000 2 29 '
    # Fields for the primary postal address:
    browser.getControl('address prefix').value = u'c/o Mama'
    browser.getControl('street').value = u'Demoweg 23'
    browser.getControl('city', index=0).value = u'Testhausen'
    browser.getControl('zip').value = u'99999'
    browser.getControl('country').displayValue = ['Austria']
    # The primary phone number:
    browser.getControl('number').value = u'112'
    # The primary e-mail address:
    browser.getControl('e-mail address').value = 'hans@example.com'
    # The primary home page address:
    browser.getControl('URL').value = 'http://www.example.com'
    # After filling out the fields correctly, we can add the record to the
    # database and get back to the address book where the entry is
    # displayed:
    browser.getControl('Add').click()
    assert '"Tester, Hans" added.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    assert (['Tester', 'Hans'] ==
            browser.etree.xpath('//table/tbody/tr/td/a/text()'))


@pytest.mark.parametrize('loginname', [
    'visitor',
    'archivist',
    'archive-visitor'])
def test_person__PersonAddForm__2(address_book, browser, loginname):
    """It cannot be accessed by some roles."""
    browser.login(loginname)
    browser.assert_forbidden(browser.PERSON_ADD_URL)


def test_person__PersonAddForm__3(address_book, browser):
    """`PersonAddForm` validates the input fields."""
    browser.login('editor')
    browser.open(browser.PERSON_ADD_URL)
    # Person and address data are relatively complex. There are some
    # required fields which lead to an error message when they are not
    # filled. Some fields get parsed, so entering rubbish leads also to an
    # error message. (Note: Germany is by default selected as country.
    # Clicking on it, deselects it, so no country is selected afterwards.):
    browser.getControl('birth date').value = u'qqqqq'
    browser.getControl('e-mail address').value = u'qqqqq'
    browser.getControl('URL').value = 'qqqqq'
    browser.getControl('Germany').click()  # deselects the default selection
    browser.getControl('Add').click()
    assert [] == browser.message
    assert browser.PERSON_ADD_URL == browser.url
    assert (['Required input is missing.',
             "The datetime string did not match the pattern u'yyyy MMM d '.",
             'Constraint not satisfied',
             'The specified URI is not valid.'] ==
            browser.etree.xpath('//ul[@class="errors"]/li/div/text()'))


def test_person__PersonAddForm__4(address_book, FieldFactory, browser):
    """User defined fields show up in the person add form."""
    FieldFactory(address_book, IPerson, 'TextLine', u'baz')
    browser.login('editor')
    browser.open(browser.PERSON_ADD_URL)
    browser.getControl('last name').value = 'Tester'
    assert '' == browser.getControl('baz').value
    browser.getControl('baz').value = 'monster'
    browser.getControl('Add').click()
    assert '"Tester" added.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url


def test_person__PersonAddForm__5(address_book, FieldFactory, browser):
    """An `editor` can enter values in user defined field in the add form."""
    FieldFactory(address_book, IPerson, 'TextLine', u'foobar')
    browser.login('editor')
    browser.open(browser.PERSON_ADD_URL)
    browser.getControl('last name').value = 'Bester'
    assert '' == browser.getControl('foobar').value
    browser.getControl('foobar').value = 'better'
    browser.getControl('Add').click()
    assert '"Bester" added.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    # The entered value got persisted:
    browser.getLink('Bester').click()
    assert browser.PERSON_EDIT_URL == browser.url
    assert 'better' == browser.getControl('foobar').value


@pytest.mark.parametrize('username', ('editor', 'mgr'))
def test_person__PersonAddForm__6(
        address_book, FieldFactory, browser2, browser, username):
    """A deleted field is not displayed any more in the add form."""
    delete_field(
        browser2,
        FieldFactory(address_book, IPerson, 'TextLine', u'foobar').__name__)
    browser.login(username)
    browser.open(browser.PERSON_ADD_URL)
    with pytest.raises(LookupError):
        browser.getControl('foobar')


def test_person__PersonAddForm__7(address_book, KeywordFactory, browser):
    """A keyword can be assigned using `PersonAddForm`."""
    KeywordFactory(address_book, u'friend')
    KeywordFactory(address_book, u'Company co-worker')
    family = KeywordFactory(address_book, u'family')
    church = KeywordFactory(address_book, u'church')
    browser.login('editor')
    browser.open(browser.PERSON_ADD_URL)
    browser.getControl('last name').value = 'keyword test'
    # In browser tests keywords are selected using a simple multiselect widget
    # because the testbrowser does not support JavaScript. The widget currently
    # displays all existing keywords case insensitive alphabetically sorted.
    assert ['church',
            'Company co-worker',
            'family',
            'friend'] == browser.getControl('keywords').displayOptions
    # Keyword assignments are stored when saving:
    browser.getControl('church').click()
    browser.getControl('family').click()
    browser.getControl('Add').click()
    assert '"keyword test" added.' == browser.message
    with zope.component.hooks.site(address_book):
        assert set([church, family]) == set(address_book['Person'].keywords)


def test_person__PersonAddForm__8(address_book, browser):
    """`PersonAddForm` uses the default entity and field sort order."""
    browser.login('editor')
    browser.open(browser.PERSON_ADD_URL)
    assert ['Person.first_name',
            'Person.last_name',
            'Person.birth_date',
            'Person.keywords:list',
            'Person.notes',
            'Postaladdress.address_prefix',
            'Postaladdress.street',
            'Postaladdress.city',
            'Postaladdress.zip',
            'Postaladdress.country:list',
            'Phonenumber.number',
            'Emailaddress.email',
            'Homepageaddress.url',
            'buttons.add',
            'buttons.cancel'] == form_fields_names(browser)


def test_person__PersonAddForm__9(address_book, browser):
    """`PersonAddForm` respects the the user defined entity sort order."""
    browser.login('editor')
    postal_address_entity = IEntity(IPostalAddress)
    order = zope.component.getUtility(IEntityOrder)
    # When moving the postal address two positions up, the sort order in the
    # person add form changes accordingly:
    order.up(postal_address_entity, delta=2)
    browser.open(browser.PERSON_ADD_URL)
    assert ['Postaladdress.address_prefix',
            'Postaladdress.street',
            'Postaladdress.city',
            'Postaladdress.zip',
            'Postaladdress.country:list',
            'Person.first_name',
            'Person.last_name',
            'Person.birth_date',
            'Person.keywords:list',
            'Person.notes',
            'Phonenumber.number',
            'Emailaddress.email',
            'Homepageaddress.url',
            'buttons.add',
            'buttons.cancel'] == form_fields_names(browser)


def test_person__PersonAddForm__10(translated_address_book, browser):
    """`PersonAddForm` translates country names."""
    browser.login('editor')
    browser.lang('de-DE')
    browser.open(browser.PERSON_ADD_URL)
    assert ['Deutschland'] == browser.getControl('Land').displayValue
    browser.getControl('Land').displayValue = ['Schweiz']
    browser.getControl('Ort').value = 'Thun'
    browser.getControl('Familienname').value = 'Deutsch'
    browser.getControl(u'Hinzufügen').click()
    assert u'„Deutsch“ hinzugefügt.' == browser.message


def test_person__PersonAddForm__11(translated_address_book, browser):
    """`PersonAddForm` translates error messages using `zope.app.locales`."""
    # This test makes sure that `zope.app.locales` is installed.
    browser.login('editor')
    browser.lang('de-DE')
    browser.open(browser.PERSON_ADD_URL)
    browser.getControl(u'Hinzufügen').click()
    assert ['Erforderliche Eingabe fehlt.'] == browser.etree.xpath(
        '//ul[@class="errors"]/li/div/text()')


def test_person__PersonAddForm__12(address_book, browser):
    """It requires birth dates after 1900."""
    browser.login('editor')
    browser.open(browser.PERSON_ADD_URL)
    browser.getControl('last name').value = 'Tester'
    browser.getControl('birth date').value = '1899 12 31 '
    browser.getControl('Add').click()
    assert ['Value is too small'] == browser.etree.xpath(
        '//ul[@class="errors"]/li/div/text()')


def test_person__PersonAddForm__13(address_book, FieldFactory, browser):
    """It prevents entering date values before 1900 in a user defined field."""
    FieldFactory(address_book, IPerson, 'Date', u'my date')
    browser.login('editor')
    browser.open(browser.PERSON_ADD_URL)
    browser.getControl('last name').value = 'Bester'
    browser.getControl('my date').value = '1899 12 31 '
    browser.getControl('Add').click()
    assert ['Value is too small'] == browser.etree.xpath(
        '//ul[@class="errors"]/li/div/text()')


def test_person__AddGroup__1(address_book, browser):
    """`AddGroup` respects the user definded field sort order."""
    browser.login('editor')
    person_entity = IEntity(IPerson)
    # When switching the first name and the last name of the person the person
    # add form changes accordingly:
    person_entity.setFieldOrder(('last_name', 'first_name'))
    browser.open(browser.PERSON_ADD_URL)
    assert ['Person.last_name',
            'Person.first_name',
            'Person.birth_date',
            'Person.keywords:list',
            'Person.notes',
            'Postaladdress.address_prefix',
            'Postaladdress.street',
            'Postaladdress.city',
            'Postaladdress.zip',
            'Postaladdress.country:list',
            'Phonenumber.number',
            'Emailaddress.email',
            'Homepageaddress.url',
            'buttons.add',
            'buttons.cancel'] == form_fields_names(browser)


def test_person__PersonEditForm__1(person_data, browser):
    """`PersonEditForm` allows to change person's data."""
    browser.login('editor')
    browser.open(browser.PERSONS_LIST_URL)
    browser.getLink('Tester').click()
    # The table entry is a link which leads to the edit page of the person
    # where the data of the person is displayed:
    assert browser.PERSON_EDIT_URL == browser.url
    assert 'Petra' == browser.getControl('first name').value
    assert 'Tester' == browser.getControl('last name').value
    assert 'c/o Mama' == browser.getControl('address prefix', index=0).value
    assert '+4901767654321' == browser.getControl('number', index=1).value
    # The last modification date is also displayed:
    assert '<legend>metadata</legend>' in browser.contents
    assert '<span>Modification Date (UTC)</span>' in browser.contents
    # Changed values get persisted when selecting `Save`:
    browser.getControl('first name').value = u'Peter'
    browser.getControl('birth date').value = '2001 1 1 '
    browser.getControl('zip', index=0).value = u'99991'
    browser.getControl('e-mail address', index=1).value = u'petra9@example.com'
    browser.getControl('URL', index=0).value = 'http://petra23.example.com'
    browser.getControl('number', index=1).value = u'110'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    assert (['Tester', 'Peter'] ==
            browser.etree.xpath('//table/tbody/tr/td/a/text()'))
    # The changes show up in the edit form, too:
    browser.open(browser.PERSON_EDIT_URL)
    assert 'Peter' == browser.getControl('first name').value
    assert 'Tester' == browser.getControl('last name').value
    assert '2001 1 1 ' == browser.getControl('birth date').value
    assert '99991' == browser.getControl('zip', index=0).value
    assert 'petra9@example.com' == browser.getControl(
        'e-mail address', index=1).value
    assert ('http://petra23.example.com' ==
            browser.getControl('URL', index=0).value)
    assert '110' == browser.getControl('number', index=1).value


def test_person__PersonEditForm__2(person_data, browser):
    """`PersonEditForm` allows to cancel changes in person's data."""
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    # If the user edits and decides to discard his changes he can choose the
    # cancel button and is set back to the address book overview. The
    # changes were not saved:
    browser.getControl('first name').value = u'Hans'
    browser.getControl('number', index=1).value = u'110'
    browser.getControl('Cancel').click()
    assert 'No changes were applied.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    assert (['Tester', 'Petra'] ==
            browser.etree.xpath('//table/tbody/tr/td/a/text()'))
    browser.open(browser.PERSON_EDIT_URL)
    assert 'Petra' == browser.getControl('first name').value
    assert '+4901767654321' == browser.getControl('number', index=1).value


def test_person__PersonEditForm__3(person_data, browser):
    """`PersonEditForm` validates the form input."""
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    # If the user edits and decides to save his changes he chooses the apply
    # button. If there are errors in the input data an error message is
    # displayed:
    browser.getControl('birth date').value = u'qqqq'
    browser.getControl('Save').click()
    assert [] == browser.message
    assert (
        ["The datetime string did not match the pattern u'yyyy MMM d '."] ==
        browser.etree.xpath('//ul[@class="errors"]/li/div/text()'))


def test_person__PersonEditForm__4(person_with_field_data, browser):
    """User defined fields show up on the edit form and contain their value."""
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    assert 'my value' == browser.getControl('foobar').value
    browser.getControl('foobar').value = 'monster'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    browser.getLink('Tester').click()
    assert 'monster' == browser.getControl('foobar').value
    browser.getControl('Cancel').click()
    assert 'No changes were applied.' == browser.message


def test_person__PersonEditForm__5(person_with_field_data, browser):
    """An `editor` is able to edit content in user definded fields."""
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    assert 'my value' == browser.getControl('foobar').value
    browser.getControl('foobar').value = 'editor was here'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    # The entered values got persisted:
    browser.getLink('Tester').click()
    assert browser.PERSON_EDIT_URL == browser.url
    assert 'editor was here' == browser.getControl('foobar').value


def test_person__PersonEditForm__6(person_with_field_data, browser):
    """A `visitor` is only able to see content in all kinds of fields.

    There is neither a clone button nor a delete button.

    """
    browser.login('visitor')
    browser.open(browser.PERSON_EDIT_URL)
    assert 'petra@example.com' in browser.contents
    assert 'my value' in browser.contents
    assert ['form.buttons.apply',
            'form.buttons.cancel',
            'form.buttons.export'] == browser.all_control_names


@pytest.mark.parametrize('username', ('editor', 'mgr'))
def test_person__PersonEditForm__7(
        person_with_field_data, browser2, browser, username):
    """A deleted field is not displayed any more in the edit form."""
    delete_field(browser2, 'Field-1')
    browser.login(username)
    browser.open(browser.PERSON_EDIT_URL)
    with pytest.raises(LookupError):
        browser.getControl('foobar')


def test_person__PersonEditForm__8(person_with_field_data, browser2, browser):
    """A deleted field is not displayed any more in the edit form."""
    delete_field(browser2, 'Field-1')
    browser.login('visitor')
    browser.open(browser.PERSON_EDIT_URL)
    assert 'foobar' not in browser.contents


def test_person__PersonEditForm__9(person_data, browser):
    """A keyword can be assigned using `PersonEditForm`."""
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getControl('last name').value = 'keyword test'
    # Keyword assignments are stored when saving:
    assert browser.getControl('church').selected
    assert browser.getControl('family').selected
    browser.getControl('church').click()
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    address_book = person_data
    family = address_book.keywords.get_keyword_by_title(u'family')
    with zope.component.hooks.site(address_book):
        assert set([family]) == set(address_book['Person'].keywords)


def test_person__PersonEditForm__10(person_data, browser):
    """`PersonEditForm` shows entities and fields in default sort order."""
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    assert ['Person_0.first_name',
            'Person_0.last_name',
            'Person_0.birth_date',
            'Person_0.keywords:list',
            'Person_0.notes',
            'defaults.default_postal_address:list',
            'defaults.default_phone_number:list',
            'defaults.default_email_address:list',
            'defaults.default_home_page_address:list',
            'Postaladdress_0.address_prefix',
            'Postaladdress_0.street',
            'Postaladdress_0.city',
            'Postaladdress_0.zip',
            'Postaladdress_0.country:list',
            'Postaladdress_1.address_prefix',
            'Postaladdress_1.street',
            'Postaladdress_1.city',
            'Postaladdress_1.zip',
            'Postaladdress_1.country:list',
            'Phonenumber_0.number',
            'Phonenumber_1.number',
            'Emailaddress_0.email',
            'Emailaddress_1.email',
            'Homepageaddress_0.url',
            'Homepageaddress_1.url',
            'buttons.apply',
            'buttons.clone_person',
            'buttons.archive_person',
            'buttons.delete_person',
            'buttons.delete_entry',
            'buttons.export',
            'buttons.cancel'] == form_fields_names(browser)


def test_person__PersonEditForm__11(person_data, browser):
    """`PersonEditForm` respects the user defined entity  sort order."""
    browser.login('editor')
    person_entity = IEntity(IPerson)
    with zope.component.hooks.site(person_data):
        order = zope.component.getUtility(IEntityOrder)
        # When moving the person one position down, the sort order changes
        # accordingly:
        order.down(person_entity, delta=1)
    browser.open(browser.PERSON_EDIT_URL)
    assert ['defaults.default_postal_address:list',
            'defaults.default_phone_number:list',
            'defaults.default_email_address:list',
            'defaults.default_home_page_address:list',
            'Person_0.first_name',
            'Person_0.last_name',
            'Person_0.birth_date',
            'Person_0.keywords:list',
            'Person_0.notes',
            'Postaladdress_0.address_prefix',
            'Postaladdress_0.street',
            'Postaladdress_0.city',
            'Postaladdress_0.zip',
            'Postaladdress_0.country:list',
            'Postaladdress_1.address_prefix',
            'Postaladdress_1.street',
            'Postaladdress_1.city',
            'Postaladdress_1.zip',
            'Postaladdress_1.country:list',
            'Phonenumber_0.number',
            'Phonenumber_1.number',
            'Emailaddress_0.email',
            'Emailaddress_1.email',
            'Homepageaddress_0.url',
            'Homepageaddress_1.url',
            'buttons.apply',
            'buttons.clone_person',
            'buttons.archive_person',
            'buttons.delete_person',
            'buttons.delete_entry',
            'buttons.export',
            'buttons.cancel'] == form_fields_names(browser)


def test_person__PersonEditForm__12(address_book, UserFactory, browser):
    """It does not render the following buttons for a person who is a user:

    * delete button
    * archive button
    """
    UserFactory(address_book, u'Andronicus', u'Loscher', u'l@scher.de',
                u'7zhn8ujm', ['Visitor'])
    browser.login('mgr')
    browser.open(browser.PERSON_EDIT_URL)
    assert ['form.buttons.apply',
            'form.buttons.cancel',
            'form.buttons.clone_person',
            'form.buttons.delete_entry',
            'form.buttons.export'] == browser.submit_control_names


def test_person__PersonEditForm__13(
        address_book, FullPersonFactory, FileFactory, browser):
    """It allows to change the name and mimetype of a file entity."""
    FileFactory(FullPersonFactory(address_book, u'Test'), u'my-file.txt',
                data='boring text')
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getControl('name', index=2).value = 'my nice file.txt'
    browser.getControl('Mime Type').value = 'text/example'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url


def test_person__PersonEditForm__14(
        address_book, FullPersonFactory, FileFactory, browser, tmpfile):
    """It allows to upload a new file.

    This changes the name and the mime type if necessary. When the browser does
    not know the mime type and sends ``application/octet-stream``, the mime
    type is guessed using the file extension and file contents.

    """
    FileFactory(FullPersonFactory(address_book, u'Test'), u'my-file.txt',
                data='boring text')
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    fh, filename = tmpfile('special data, blah', '.js')
    browser.getControl('file', index=1).add_file(
        fh, 'application/octet-stream', filename)
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    # The downloaded file behaves accordingly:
    browser.open(browser.PERSON_EDIT_URL)
    assert browser.getControl('file name').value == filename
    assert 'application/javascript' == browser.getControl('Mime Type').value


def test_person__PersonEditForm__15(
        address_book, FullPersonFactory, FileFactory, browser, tmpfile):
    """It correctly handles a missing mime-type.

    The mime type is optional, if the browser of the client does not send
    a content type and zope.mimetype can't determine the mime type from
    the filename or file content, it is set to ``application/octet-stream``.

    """
    FileFactory(FullPersonFactory(address_book, u'Test'), u'my-file.txt',
                data='boring text')
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    fh, filename = tmpfile('Ä, no content type, huh', '')
    browser.getControl('file', index=1).add_file(fh, '', filename)
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    browser.open(browser.PERSON_EDIT_URL)
    assert 'application/octet-stream' == browser.getControl('Mime Type').value


def test_person__PersonEditForm__16(
        address_book, FieldFactory, FullPersonFactory, FileFactory, browser):
    """The data in the user defined field on a file can be edited."""
    field_name = FieldFactory(address_book, IFile, 'Text', u'mynotes').__name__
    person = FullPersonFactory(address_book, u'Tester')
    FileFactory(person, **{'filename': u'foo.txt', field_name: 'first letter'})
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    assert 'first letter' == browser.getControl('mynotes').value
    browser.getControl('mynotes').value = 'second letter'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    browser.getLink('Tester').click()
    assert 'second letter' == browser.getControl('mynotes').value


def test_person__PersonEditForm__17(
        address_book, FullPersonFactory, FileFactory, browser):
    """A visitor is not able to edit a file."""
    FileFactory(FullPersonFactory(address_book, u'Test'), u'my-file.txt',
                data='boring text')
    browser.login('visitor')
    browser.open(browser.PERSON_EDIT_URL)
    # There are neither any input widgets nor a delete button:
    assert ['form.buttons.apply',
            'form.buttons.cancel',
            'form.buttons.export'] == browser.all_control_names


@pytest.mark.parametrize('login', ('archivist', 'archive-visitor'))
def test_person__PersonEditForm__18(
        address_book, FullPersonFactory, browser, login):
    """It cannot be accessed by some roles."""
    FullPersonFactory(address_book, u'Test')
    browser.login(login)
    browser.assert_forbidden(browser.PERSON_EDIT_URL)


def test_person__PersonEditForm__19(
        address_book, FullPersonFactory, browser, browser_request):
    """It does not render the `archive` button if the tab is deselected."""
    address_book.deselected_tabs = {'Archive'}
    FullPersonFactory(address_book, u'Test')
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    assert [
        'form.buttons.apply',
        'form.buttons.cancel',
        'form.buttons.clone_person',
        'form.buttons.delete_entry',
        'form.buttons.delete_person',
        'form.buttons.export'] == browser.submit_control_names


def test_person__PersonEditGroup__1(person_data, browser):
    """`PersonEditGroup` respects the user defined field sort order."""
    browser.login('editor')
    postal_address_entity = IEntity(IPostalAddress)
    # When switching the address prefix and the street name of the postal
    # address the person edit form changes accordingly:
    with zope.component.hooks.site(person_data):
        postal_address_entity.setFieldOrder(('street', 'address_prefix'))
    browser.open(browser.PERSON_EDIT_URL)
    assert ['Person_0.first_name',
            'Person_0.last_name',
            'Person_0.birth_date',
            'Person_0.keywords:list',
            'Person_0.notes',
            'defaults.default_postal_address:list',
            'defaults.default_phone_number:list',
            'defaults.default_email_address:list',
            'defaults.default_home_page_address:list',
            'Postaladdress_0.street',
            'Postaladdress_0.address_prefix',
            'Postaladdress_0.city',
            'Postaladdress_0.zip',
            'Postaladdress_0.country:list',
            'Postaladdress_1.street',
            'Postaladdress_1.address_prefix',
            'Postaladdress_1.city',
            'Postaladdress_1.zip',
            'Postaladdress_1.country:list',
            'Phonenumber_0.number',
            'Phonenumber_1.number',
            'Emailaddress_0.email',
            'Emailaddress_1.email',
            'Homepageaddress_0.url',
            'Homepageaddress_1.url',
            'buttons.apply',
            'buttons.clone_person',
            'buttons.archive_person',
            'buttons.delete_person',
            'buttons.delete_entry',
            'buttons.export',
            'buttons.cancel'] == form_fields_names(browser)


def test_person__PersonEditGroup__2(address_book, FullPersonFactory, browser):
    """`PersonEditGroup` stores modification date only for changed entries."""
    # To ease the comparisons in the test we set all modification dates to a
    # default value:
    person = FullPersonFactory(address_book, u'Tester')
    dt = set_modified(person, 2000, 1, 1)
    for entry in person.values():
        set_modified(entry, 2000, 1, 1)
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getControl('city').value = 'Heretown'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    assert IZopeDublinCore(person).modified == dt
    assert IZopeDublinCore(person['PhoneNumber']).modified == dt
    assert IZopeDublinCore(person['HomePageAddress']).modified == dt
    assert IZopeDublinCore(person['EMailAddress']).modified == dt
    # Only postal address has a changed modification date:
    assert IZopeDublinCore(person['PostalAddress']).modified != dt


def test_person__PersonEditGroup__3(address_book, FullPersonFactory, browser):
    """`PersonEditGroup` does not alter entity mod-dates if person changed."""
    # To ease the comparisons in the test we set all modification dates to a
    # default value:
    person = FullPersonFactory(address_book, u'Tester')
    dt = set_modified(person, 2000, 1, 1)
    for entry in person.values():
        set_modified(entry, 2000, 1, 1)
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getControl('first name').value = 'Hans'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    # Only person has a changed modification date:
    assert IZopeDublinCore(person).modified != dt
    assert IZopeDublinCore(person['PhoneNumber']).modified == dt
    assert IZopeDublinCore(person['HomePageAddress']).modified == dt
    assert IZopeDublinCore(person['EMailAddress']).modified == dt
    assert IZopeDublinCore(person['PostalAddress']).modified == dt


def test_person__ArchivePersonForm__1(address_book, PersonFactory, browser):
    """It archives a person."""
    PersonFactory(address_book, u'Tester')
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getControl('Archive person').click()
    assert browser.PERSON_ARCHIVE_URL == browser.url
    browser.getControl('Yes, archive').click()
    assert '"Tester" archived.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    assert 'There are no persons' in browser.contents


def test_person__ArchivePersonForm__2(address_book, PersonFactory, browser):
    """It allows to abort archiving."""
    PersonFactory(address_book, u'Tester')
    browser.login('editor')
    browser.open(browser.PERSON_ARCHIVE_URL)
    browser.getControl('No, cancel').click()
    assert browser.PERSON_EDIT_URL == browser.url
    assert 'Tester' in browser.contents
    assert 'Archiving canceled.' == browser.message


@pytest.mark.parametrize('loginname', [
    'visitor',
    'archivist',
    'archive-visitor'])
def test_person__ArchivePersonForm__3(
        address_book, FullPersonFactory, browser, loginname):
    """It cannot be accessed by some roles."""
    FullPersonFactory(address_book, u'Test')
    browser.login(loginname)
    browser.assert_forbidden(browser.PERSON_ARCHIVE_URL)


def test_person__ArchivePersonForm__4(address_book, UserFactory, browser):
    """It renders an error message on direct access for users leads.

    Aka persons which are registered as users of the address book.
    """
    UserFactory(address_book, u'Andronicus', u'Loscher', u'l@scher.de',
                u'7zhn8ujm', ['Visitor'])
    browser.login('mgr')
    browser.open(browser.PERSON_ARCHIVE_URL)
    browser.handleErrors = False
    browser.getControl('Yes').click()
    assert ('Failed to archive person: This person is referenced. To archive'
            ' this person, remove the reference before.' == browser.message)
    assert browser.PERSONS_LIST_URL == browser.url
    assert 'Loscher' in browser.contents


def test_person__ClonePersonForm__1(person_with_field_data, browser):
    """`ClonePersonForm` allows to clone a person and its data."""
    # As user defined fields and keywords may behave unusual, let's create
    # some:
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getControl('Clone person').click()
    assert browser.PERSON_CLONE_URL == browser.url
    browser.getControl('Yes').click()
    assert '"Tester, Petra" cloned.' == browser.message

    # The URL has changed as the cloned Person gets now edited, but the
    # entered data is still the same:
    assert browser.PERSON_EDIT_URL + '-2' == browser.url
    assert 'Tester' == browser.getControl('last name').value
    assert 'Petra' == browser.getControl('first name').value
    assert ['church', 'family'] == browser.getControl('keywords').displayValue
    assert 'my value' == browser.getControl('foobar').value
    assert 'petra@example.com' == browser.getControl('e-mail', index=1).value
    assert '+4901767654321' == browser.getControl('number', index=1).value
    assert ('http://petra.example.com' ==
            browser.getControl('URL', index=0).value)

    # Changing data in the clone does not change the original:
    browser.getControl('last name').value = 'Testerella'
    browser.getControl('first name').value = 'Marta'
    browser.getControl('keywords').displayValue = ['friend']
    browser.getControl('foobar').value = 'other value'
    browser.getControl('e-mail', index=1).value = 'm@test333.de'
    browser.getControl('number', index=1).value = '333'
    browser.getControl('URL', index=0).value = 'http://test333.de'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    browser.getLink('Tester').click()
    assert 'Tester' == browser.getControl('last name').value
    assert 'Petra' == browser.getControl('first name').value
    assert ['church', 'family'] == browser.getControl('keywords').displayValue
    assert 'my value' == browser.getControl('foobar').value
    assert 'petra@example.com' == browser.getControl('e-mail', index=1).value
    assert '+4901767654321' == browser.getControl('number', index=1).value
    assert ('http://petra.example.com' ==
            browser.getControl('URL', index=0).value)

    # Changing data in the original does not change the clone:
    browser.getControl('last name').value = 'Testr'
    browser.getControl('keywords').displayValue = ['church', 'friend']
    browser.getControl('foobar').value = 'your value'
    browser.getControl('number', index=1).value = '012354-234234-23'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    browser.getLink('Testerella').click()
    assert 'Testerella' == browser.getControl('last name').value
    assert 'Marta' == browser.getControl('first name').value
    assert ['friend'] == browser.getControl('keywords').displayValue
    assert 'other value' == browser.getControl('foobar').value
    assert 'm@test333.de' == browser.getControl('e-mail', index=1).value
    assert '333' == browser.getControl('number', index=1).value
    assert 'http://test333.de' == browser.getControl('URL', index=0).value


@pytest.mark.parametrize('loginname', [
    'visitor',
    'archivist',
    'archive-visitor'])
def test_person__ClonePersonForm__2(
        address_book, FullPersonFactory, browser, loginname):
    """It cannot be accessed by some roles."""
    FullPersonFactory(address_book, u'Test')
    browser.login(loginname)
    browser.assert_forbidden(browser.PERSON_CLONE_URL)


def test_person__DefaultSelectGroup__1(person_data, browser):
    """`DefaultSelectGroup` allows to change the default addresses."""
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    # There is always one main address of each kind (by default the first
    # one created). All addresses of each kind are displayed in a drop-down:
    assert(
        ['c/o Mama, Demoweg 23, 88888, Testhausen, Austria',
         'RST-Software, Forsterstraße 302a, 98344, Erfurt, Germany'] ==
        browser.getControl('main postal address').displayOptions)
    assert (['c/o Mama, Demoweg 23, 88888, Testhausen, Austria'] ==
            browser.getControl('main postal address').displayValue)

    assert (['+4901767654321', '+4901761234567'] ==
            browser.getControl('main phone number').displayOptions)
    assert (['+4901767654321'] ==
            browser.getControl('main phone number').displayValue)

    assert (['petra@example.com', 'pt@rst.example.edu'] ==
            browser.getControl('main e-mail address').displayOptions)
    assert (['petra@example.com'] ==
            browser.getControl('main e-mail address').displayValue)

    assert (['http://petra.example.com',
             'http://www.rst.example.edu'] ==
            browser.getControl('main home page address').displayOptions)
    assert (['http://petra.example.com'] ==
            browser.getControl('main home page address').displayValue)
    # Set the other addresses as default:

    browser.getControl('main postal address').displayValue = [
        'RST-Software, Forsterstra\xc3\x9fe 302a, 98344, Erfurt, Germany']
    browser.getControl('main e-mail address').displayValue = [
        'pt@rst.example.edu']
    browser.getControl('main home page address').displayValue = [
        'http://www.rst.example.edu']
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    browser.open(browser.PERSON_EDIT_URL)
    assert (['http://www.rst.example.edu'] ==
            browser.getControl('main home page address').displayValue)


def test_person__DefaultSelectGroup__2(person_data, browser):
    """`DefaultSelectGroup` respects the user defined entity sort order."""
    browser.login('editor')
    # The default sort order is tested in test_person__PersonEditForm__10!
    postal_address_entity = IEntity(IPostalAddress)
    with zope.component.hooks.site(person_data):
        order = zope.component.getUtility(IEntityOrder)
        # When moving the postal address one position down, the sort order
        # changes accordingly:
        order.down(postal_address_entity, delta=1)
    browser.open(browser.PERSON_EDIT_URL)
    assert (['default_phone_number',
             'default_postal_address',
             'default_email_address',
             'default_home_page_address'] ==
            [x.replace('defaults.', '').replace(':list', '')
             for x in form_fields_names(browser)
             if x.startswith('defaults.')])


def test_person__DefaultSelectGroup__3(
        translated_address_book, FullPersonFactory, browser):
    """`DefaultSelectGroup` translates country name in the address field."""
    FullPersonFactory(
        translated_address_book, u'Deutsch', postal__city=u'Thun',
        postal__country=gocept.country.db.Country('CH'))
    browser.login('editor')
    browser.lang('de-DE')
    browser.open(browser.PERSON_EDIT_URL)
    assert ['Thun, Schweiz'] == browser.getControl(
        'bevorzugte Anschrift').displayValue
    browser.getControl('Abbrechen').click()
    assert u'Keine Änderungen durchgeführt.' == browser.message


def test_person__DefaultSelectGroup__4(
        translated_address_book, FullPersonFactory, browser):
    """`DefaultSelectGroup` uses English country name if requested."""
    FullPersonFactory(
        translated_address_book, u'English', postal__city=u'Thun',
        postal__country=gocept.country.db.Country('CH'))
    browser.login('editor')
    browser.lang('en-US')
    browser.open(browser.PERSON_EDIT_URL)
    assert ['Thun, Switzerland'] == browser.getControl(
        'main postal address').displayValue


def test_person__DeleteSingleEntryForm__1(person_data, browser):
    """It allows to select an entry for delete."""
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getControl('Delete single entry').click()
    assert browser.PERSON_DELETE_ENTRY_URL == browser.url
    assert (
        ['postal address -- c/o Mama, Demoweg 23, 88888, Testhausen, Austria',
         'postal address -- RST-Software, Forsterstra\xc3\x9fe 302a, 98344,'
         ' Erfurt, Germany',
         'phone number -- +4901767654321',
         'phone number -- +4901761234567',
         'e-mail address -- petra@example.com',
         'e-mail address -- pt@rst.example.edu',
         'home page address -- http://petra.example.com',
         'home page address -- http://www.rst.example.edu'] ==
        browser.getControl('Entries').displayOptions)
    # Deletion can be cancelled:
    browser.getControl('Cancel').click()
    assert 'No changes were applied.' == browser.message
    assert browser.PERSON_EDIT_URL == browser.url


@pytest.mark.parametrize('loginname', [
    'visitor',
    'archivist',
    'archive-visitor'])
def test_person__DeleteSingleEntryForm__2(person_data, browser, loginname):
    """It cannot be accessed by some roles."""
    browser.login(loginname)
    browser.assert_forbidden(browser.PERSON_DELETE_ENTRY_URL)


def test_person__DeleteSingleEntryForm__3(person_data, browser):
    """It shows an error message if no entry is selected."""
    browser.login('editor')
    browser.open(browser.PERSON_DELETE_ENTRY_URL)
    browser.getControl('Entries').displayValue = []
    browser.getControl('Delete entry').click()
    assert 'There were some errors.' in browser.contents
    assert 'Required input is missing.' in browser.contents
    assert browser.PERSON_DELETE_ENTRY_URL == browser.url


def test_person__DeletePersonForm__1(person_data, browser):
    """`DeletePersonForm` allows to delete a whole person."""
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getControl('Delete whole person').click()
    assert browser.PERSON_DELETE_URL == browser.url
    browser.getControl('Yes').click()
    assert '"Tester, Petra" deleted.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    browser.open(browser.url)  # simulate reload to get rid of the delete msg
    assert 'Petra' not in browser.contents


def test_person__DeletePersonForm__2(person_data, browser):
    """`DeletePersonForm` can be cancelled."""
    browser.login('editor')
    browser.open(browser.PERSON_DELETE_URL)
    browser.getControl('No, cancel').click()
    assert 'Deletion canceled.' == browser.message
    assert browser.PERSON_EDIT_URL == browser.url


@pytest.mark.parametrize('loginname', [
    'visitor',
    'archivist',
    'archive-visitor'])
def test_person__DeletePersonForm__3(person_data, browser, loginname):
    """It cannot be accessed by some roles."""
    browser.login(loginname)
    browser.assert_forbidden(browser.PERSON_DELETE_URL)


def test_person__DeletePersonForm__4(address_book, UserFactory, browser):
    """Directly accessing `DeletePersonForm` for user leads to an error msg."""
    UserFactory(address_book, u'Andronicus', u'Loscher', u'l@scher.de',
                u'7zhn8ujm', ['Visitor'])
    browser.login('mgr')
    browser.open(browser.PERSON_DELETE_URL)
    browser.getControl('Yes').click()
    assert ('Failed to delete person: This person is referenced. To delete '
            'this person, remove the reference before.' == browser.message)
    assert browser.PERSONS_LIST_URL == browser.url
    assert 'Loscher' in browser.contents

from icemac.addressbook.interfaces import IEntityOrder, IEntity
from icemac.addressbook.interfaces import IPerson, IPhoneNumber
from icemac.addressbook.testing import delete_field
import pytest
import zope.component


def test_browser__CategoryEditForm__1(address_book, browser):
    """`CategoryEditForm` shows an error message on a too little batch size."""
    # The minimum batch size is 1, otherwise an error message is displayed:
    browser.login('visitor')
    browser.open(browser.PREFS_URL)
    browser.getControl('batch size').value = '0'
    browser.getControl('Save').click()
    assert [] == browser.message
    assert browser.url.startswith(browser.PREFS_URL)
    assert (['Value is too small'] ==
            browser.etree.xpath('//ul[@class="errors"]/li/div/text()'))


def test_browser__CategoryEditForm__2(address_book, FieldFactory, browser):
    """`CategoryEditForm` renders user defined field names in `order_by`."""
    FieldFactory(address_book, IPerson, u'Bool', u'photo permission?')
    browser.login('visitor')
    browser.open(browser.PREFS_URL)
    assert (
        ['person -- first name',
         'person -- last name',
         'person -- birth date',
         'person -- keywords',
         'person -- notes',
         'person -- photo permission?',  # <-- here is the created field
         'postal address -- address prefix',
         'postal address -- street',
         'postal address -- city',
         'postal address -- zip',
         'postal address -- country',
         'phone number -- number',
         'e-mail address -- e-mail address',
         'home page address -- URL'] ==
        browser.getControl('order by').displayOptions)


def test_browser__CategoryEditForm__3(
        address_book, FieldFactory, browser, browser2):
    """`CategoryEditForm` omits deleted user defined fields in `order_by`."""
    field = FieldFactory(
        address_book, IPerson, u'Bool', u'photo permission?').__name__
    delete_field(browser2, field)
    browser.login('visitor')
    browser.open(browser.PREFS_URL)
    # There is no "photo permission" field here:
    assert (
        ['person -- first name',
         'person -- last name',
         'person -- birth date',
         'person -- keywords',
         'person -- notes',
         'postal address -- address prefix',
         'postal address -- street',
         'postal address -- city',
         'postal address -- zip',
         'postal address -- country',
         'phone number -- number',
         'e-mail address -- e-mail address',
         'home page address -- URL'] ==
        browser.getControl('order by').displayOptions)


def test_browser__CategoryEditForm__4(
        address_book, FieldFactory, browser, browser2):
    """`CategoryEditForm` renders a marker for

    * previously selected but
    * than deleted user defined field in `order_by`.
    """
    field = FieldFactory(
        address_book, IPerson, u'Bool', u'photo permission?').__name__
    browser.login('visitor')
    browser.open(browser.PREFS_URL)
    browser.getControl('order by').displayValue = [
        'person -- photo permission?']
    browser.handleErrors = False
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message

    delete_field(browser2, field)
    browser.open(browser.PREFS_URL)
    # There is a place holder for the deleted "photo permission" field, so UI
    # does not break:
    assert (
        ['person -- first name',
         'person -- last name',
         'person -- birth date',
         'person -- keywords',
         'person -- notes',
         'postal address -- address prefix',
         'postal address -- street',
         'postal address -- city',
         'postal address -- zip',
         'postal address -- country',
         'phone number -- number',
         'e-mail address -- e-mail address',
         'home page address -- URL',
         'Missing: IcemacAddressbookPersonPerson###Field-1'] ==
        browser.getControl('order by').displayOptions)
    # The deleted field is still selected:
    assert (['Missing: IcemacAddressbookPersonPerson###Field-1'] ==
            browser.getControl('order by').displayValue)


def test_browser__CategoryEditForm__5(address_book, browser):
    """`CategoryEditForm` allows to cancel editing."""
    browser.login('visitor')
    browser.open(browser.PREFS_URL)
    batch_size = browser.getControl('batch size').value
    browser.getControl('batch size').value = '1000'
    browser.getControl('Cancel').click()
    assert 'No changes were applied.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    browser.open(browser.PREFS_URL)
    assert batch_size == browser.getControl('batch size').value


def test_browser__CategoryEditForm__6(address_book, browser):
    """`CategoryEditForm` stores selected columns."""
    browser.login('visitor')
    browser.open(browser.PREFS_URL)
    browser.getControl('columns').displayValue = [
        'person -- birth date',
        'person -- first name',
        'person -- last name',
    ]
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    browser.open(browser.PREFS_URL)
    # The non-JS wigdet variant cannot store the items in the selected order.
    # This is an HTML issue.
    assert ([
        'person -- last name',
        'person -- first name',
        'person -- birth date',
    ] == browser.getControl('columns').displayValue)


def test_browser__CategoryEditForm__7(address_book, browser):
    """`CategoryEditForm` is not accessible for anonymous users."""
    browser.open(browser.PREFS_URL)
    assert (
        'http://localhost/ab/@@loginForm.html?camefrom=http%3A%2F%2F'
        'localhost%2Fab%2F%2B%2Bpreferences%2B%2B%2Fab%2F%40%40index.html' ==
        browser.url)


@pytest.mark.parametrize('role', ['mgr', 'editor', 'visitor'])
def test_browser__CategoryEditForm__8(address_book, browser, role):
    """`CategoryEditForm` is accessible for all kinds of logged-in users."""
    browser.login(role)
    browser.open(browser.PREFS_URL)
    # The form is displayed:
    assert (['ascending (A-->Z)', 'descending (Z-->A)'] ==
            browser.getControl('sort direction').displayOptions)


def test_browser__CategoryEditForm__9(address_book, browser, browser2):
    """`CategoryEditForm` stores preferences separately for each user."""
    browser.login('visitor')
    browser.open(browser.PREFS_URL)
    assert (['ascending (A-->Z)'] ==
            browser.getControl('sort direction').displayValue)
    browser.getControl('sort direction').displayValue = ['descending (Z-->A)']
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    browser.open(browser.PREFS_URL)
    assert (['descending (Z-->A)'] ==
            browser.getControl('sort direction').displayValue)

    browser2.login('editor')
    browser2.open(browser.PREFS_URL)
    assert (['ascending (A-->Z)'] ==
            browser2.getControl('sort direction').displayValue)


def test_browser__CategoryEditForm__10(address_book, browser):
    """The columns field of `CategoryEditForm` uses the default sort order."""
    browser.login('visitor')
    browser.open(browser.PREFS_URL)
    assert ([
        'person -- last name',
        'person -- first name',
        'person -- birth date',
        'person -- keywords',
        'person -- notes',
        'postal address -- address prefix',
        'postal address -- street',
        'postal address -- city',
        'postal address -- zip',
        'postal address -- country',
        'phone number -- number',
        'e-mail address -- e-mail address',
        'home page address -- URL',
    ] == browser.getControl('columns').displayOptions)


def test_browser__CategoryEditForm__11(address_book, browser):
    """The columns field of CategoryEditForm respects changes in sort order."""
    phone_number_entity = IEntity(IPhoneNumber)
    order = zope.component.getUtility(IEntityOrder)
    # When moving the phone number one position up, the sort order in the
    # columns fields changes accordingly:
    order.up(phone_number_entity)
    browser.login('visitor')
    browser.open(browser.PREFS_URL)
    assert ([
        'person -- last name',
        'person -- first name',
        'person -- birth date',
        'person -- keywords',
        'person -- notes',
        'phone number -- number',
        'postal address -- address prefix',
        'postal address -- street',
        'postal address -- city',
        'postal address -- zip',
        'postal address -- country',
        'e-mail address -- e-mail address',
        'home page address -- URL',
    ] == browser.getControl('columns').displayOptions)


def test_browser__CategoryEditForm__12(address_book, browser):
    """The orderBy field of `CategoryEditForm` uses the default sort order."""
    browser.login('visitor')
    browser.open(browser.PREFS_URL)
    assert ([
        'person -- first name',
        'person -- last name',
        'person -- birth date',
        'person -- keywords',
        'person -- notes',
        'postal address -- address prefix',
        'postal address -- street',
        'postal address -- city',
        'postal address -- zip',
        'postal address -- country',
        'phone number -- number',
        'e-mail address -- e-mail address',
        'home page address -- URL'] ==
        browser.getControl('order by').displayOptions)


def test_browser__CategoryEditForm__13(address_book, browser):
    """The orderBy field of CategoryEditForm respects changes in sort order."""
    phone_number_entity = IEntity(IPhoneNumber)
    order = zope.component.getUtility(IEntityOrder)
    # When moving the phone number one position down, the sort order in the
    # order by field changes accordingly:
    order.down(phone_number_entity)
    browser.login('visitor')
    browser.open(browser.PREFS_URL)
    assert ([
        'person -- first name',
        'person -- last name',
        'person -- birth date',
        'person -- keywords',
        'person -- notes',
        'postal address -- address prefix',
        'postal address -- street',
        'postal address -- city',
        'postal address -- zip',
        'postal address -- country',
        'e-mail address -- e-mail address',
        'phone number -- number',
        'home page address -- URL'] ==
        browser.getControl('order by').displayOptions)


def test_browser__CategoryEditForm__14(address_book, browser):
    """The time zone field is stored at save."""
    browser.login('visitor')
    browser.open(browser.PREFS_TIMEZONE_URL)
    browser.getControl('Time zone').displayValue = ['Europe/Berlin']
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    assert ['Europe/Berlin'] == browser.getControl('Time zone').displayValue


def test_browser__PrefGroupEditForm__redirect_to_next_url__1(
        address_book, browser):
    """`PrefGroupEditForm` redirects to self after cancel."""
    browser.login('visitor')
    browser.open(browser.PREFS_TIMEZONE_URL)
    assert ['UTC'] == browser.getControl('Time zone').displayValue
    browser.getControl('Time zone').displayValue = ['Africa/Cairo']
    browser.getControl('Cancel').click()
    # After redirect the original value is restored in the field:
    assert ['UTC'] == browser.getControl('Time zone').displayValue
    assert browser.PREFS_TIMEZONE_URL == browser.url

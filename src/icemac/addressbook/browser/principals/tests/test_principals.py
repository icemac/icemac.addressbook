# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from zope.testbrowser.browser import LinkNotFoundError
import datetime
import pytest
import pytz
import zope.component.hooks


@pytest.yield_fixture(scope='function')
def localadmin(address_book, UserFactory, browser):
    """Create an administrator inside the address book and log in him.

    Returns a browser instance.

    """
    # Using an administrator defined inside the address book to show that he
    # serves fine as administrator.
    UserFactory(address_book, 'Arne', 'Admin', 'arne@example.com', '1qay2wsx',
                ['Administrator'])
    browser.formlogin('arne@example.com', '1qay2wsx')
    # Restore site setting which the browser usage has resetted:
    with zope.component.hooks.site(address_book):
        yield browser


def test_principals__Overview__1(address_book, browser):
    """If no users are defined `Overview` shows a message telling that."""
    browser.login('mgr')
    browser.open(browser.PRINCIPALS_LIST_URL)
    # The users list is initially empty because `mgr` belongs to the global
    # users:
    assert ('No users defined yet or you are not allowed to access any' in
            browser.contents)


def test_principals__Overview__2(address_book, UserFactory, browser):
    """The roles displayed on the overview list are listed comma separated."""
    UserFactory(address_book, 'Hans', 'Tester', 'tester@example.com', 'secret',
                ['Visitor', 'Editor'])
    # The created user cannot login via BasicAuth and `editor` is not allowed
    # to see him, so we have to use `mgr`.
    browser.login('mgr')
    browser.open(browser.PRINCIPALS_LIST_URL)
    assert ['Editor, Visitor'] == browser.etree.xpath('//tr/td[3]/text()')


def test_principals__Overview__3(
        localadmin, address_book, UserFactory, browser):
    """`Overview` displays users sorted by the name column."""
    UserFactory(address_book, u'Ben', u'Utzer', u'ben.utzer@example.com',
                u'12345678', ['Visitor'])
    UserFactory(address_book, u'C.', u'Liebig', u'b@example.com',
                u'12345678', ['Visitor'])
    browser = localadmin.open(localadmin.PRINCIPALS_LIST_URL)
    assert ['Admin, Arne',
            'Liebig, C.',
            'Utzer, Ben'] == browser.etree.xpath(
                '//table/tbody/tr/td/a/text()')


@pytest.mark.parametrize('role', [u'Visitor', 'Editor', 'Archivist'])
def test_principals__Overview__4(address_book, UserFactory, browser, role):
    """It shows a non-admin only one user: himself."""
    UserFactory(address_book, u'Urs', u'Unstable', u'uu@example.com',
                'u1u2u3u4', [role])
    UserFactory(address_book, u'Urs2', u'Unstable2', u'uu2@example.com',
                'u1u2u3u4', [role])
    browser.formlogin(u'uu@example.com', 'u1u2u3u4')
    browser.open(browser.PRINCIPALS_LIST_URL)
    assert (['Unstable, Urs'] ==
            browser.etree.xpath('//table/tbody/tr/td/a/text()'))


def test_principals__Overview__5(address_book, UserFactory, browser):
    """`Overview` truncates too long notes contents."""
    user = UserFactory(
        address_book, u'Ben', u'Utzer', u'ben.utzer@example.com', u'12345678',
        ['Visitor'])
    user.description = (u'This is a new user created to show the '
                        u'truncation of too long notes in the `Overview`.')
    browser.login('mgr')
    browser.open(browser.PRINCIPALS_LIST_URL)
    assert ([u'This is a new user created to show the truncation of …'] ==
            browser.etree.xpath('//table/tbody/tr/td[5]/text()'))


def test_principals__Overview__5_5(
        address_book, UserFactory, TimeZonePrefFactory, browser):
    """It renders the last login time in user's local time zone."""
    user = UserFactory(
        address_book, u'Ben', u'Utzer', u'ben.utzer@example.com', u'12345678',
        ['Visitor'])
    user.last_login = pytz.utc.localize(datetime.datetime(2016, 6, 20, 18, 13))
    TimeZonePrefFactory('Europe/Berlin')
    browser.login('mgr')
    browser.open(browser.PRINCIPALS_LIST_URL)
    assert (['16/06/20 20:13'] ==
            browser.etree.xpath('//table/tbody/tr/td[4]/text()'))


@pytest.mark.parametrize('user', ['visitor', 'editor'])
def test_principals__Overview__6(address_book, browser, user):
    """There is no link to create a user in `Overview` for non-admin users."""
    browser.login(user)
    browser.open(browser.PRINCIPALS_LIST_URL)
    with pytest.raises(LinkNotFoundError):
        browser.getLink('user')


def test_principals__AddForm__1(
        localadmin, address_book, FullPersonFactory, browser2):
    """`AddForm` allows Administrators to create new users."""
    FullPersonFactory(address_book, u'Tester', first_name=u'Hans',
                      email__email=u'tester@example.com')
    FullPersonFactory(address_book, u'Utzer', first_name=u'Ben',
                      email__email=u'ben.utzer@example.com')
    FullPersonFactory(address_book, u'Liebig', first_name=u'B.')
    browser = localadmin.open(localadmin.PRINCIPALS_LIST_URL)
    browser.getLink('user').click()
    assert browser.PRINCIPAL_ADD_URL == browser.url
    # Only persons with a default e-mail address who are not yet users are
    # shown as possible users. (So 'B. Liebig' (no mails address) and 'Admin,
    # Arne' (already a user) are not shown.):
    assert (['Tester, Hans', 'Utzer, Ben'] ==
            browser.getControl('person').displayOptions)
    browser.getControl('person').displayValue = ['Tester, Hans']
    browser.getControl('password', index=0).value = '1234567890'
    browser.getControl('password repetition').value = '1234567890'
    browser.getControl('Archive Visitor').click()
    browser.getControl('Add').click()
    assert '"Tester, Hans" added.' == browser.message
    assert browser.PRINCIPALS_LIST_URL == browser.url
    assert (['Admin, Arne', 'Tester, Hans'] ==
            browser.etree.xpath('//td/a/text()'))

    browser2.formlogin('tester@example.com', '1234567890')
    assert 'You have been logged-in successfully.' == browser2.message
    assert browser.ADDRESS_BOOK_WELCOME_URL == browser2.url


def test_principals__AddForm__2(localadmin):
    """`AddForm` can be cancelled."""
    browser = localadmin.open(localadmin.PRINCIPAL_ADD_URL)
    browser.getControl('Cancel').click()
    assert 'Addition canceled.' == browser.message
    assert browser.PRINCIPALS_LIST_URL == browser.url


def test_principals__AddForm__3(localadmin, address_book, FullPersonFactory):
    """`AddForm` validates that password matches its repetition."""
    FullPersonFactory(address_book, u'Tester', first_name=u'Hans',
                      email__email=u'tester@example.com')
    browser = localadmin.open(localadmin.PRINCIPAL_ADD_URL)
    browser.getControl('person').displayValue = ['Tester, Hans']
    browser.getControl('password', index=0).value = '1234567890'
    browser.getControl('password repetition').value = '0123456789'
    browser.getControl('Add').click()
    assert [] == browser.message
    assert (['Entry in password field was not equal to entry in password '
             'repetition field.'] ==
            browser.etree.xpath('//div[@class="error"]/text()'))


def test_principals__AddForm__4(localadmin, address_book, FullPersonFactory):
    """`AddForm` validates that the password is not too short."""
    FullPersonFactory(address_book, u'Tester', first_name=u'Hans',
                      email__email=u'tester@example.com')
    browser = localadmin.open(localadmin.PRINCIPAL_ADD_URL)
    browser.getControl('person').displayValue = ['Tester, Hans']
    browser.getControl('password', index=0).value = '123'
    browser.getControl('password repetition').value = '123'
    browser.getControl('Add').click()
    assert [] == browser.message
    assert (['Value is too short', 'Value is too short'] ==
            browser.etree.xpath(
                '//ul[@class="errors"]/li/div[@class="error"]/text()'))


def test_principals__AddForm__5(localadmin, address_book, FullPersonFactory):
    """`AddForm` makes sure the login name of the principals stays unique."""
    FullPersonFactory(address_book, u'Admin2', first_name=u'Arne2',
                      email__email=u'arne@example.com')
    browser = localadmin.open(localadmin.PRINCIPAL_ADD_URL)
    browser.getControl('person').displayValue = ['Admin2, Arne2']
    browser.getControl('password', index=0).value = '12345678'
    browser.getControl('password repetition').value = '12345678'
    browser.getControl('Add').click()
    assert [] == browser.message
    assert (['Principal Login already taken!'] ==
            browser.etree.xpath('//div[@class="error"]/text()'))


@pytest.mark.parametrize('user', ['visitor', 'editor', 'archivist'])
def test_principals__AddForm__6(address_book, browser, user):
    """It cannot be accessed by a non-admin users."""
    browser.login(user)
    browser.assert_forbidden(browser.PRINCIPAL_ADD_URL)


def test_principals__AddForm__7(address_book, UserFactory, localadmin):
    """`AddForm` can create a new user for a person those user was deleted."""
    UserFactory(address_book, u'Urs', u'Unstable', u'uu@example.com',
                'u1u2u3u4', ['Visitor'])
    browser = localadmin.open(localadmin.PRINCIPAL_DELETE_URL)
    browser.getControl('Yes').click()
    assert '"Unstable, Urs" deleted.' == browser.message
    browser.open(browser.PRINCIPAL_ADD_URL)
    assert ['Unstable, Urs'] == browser.getControl('person').displayOptions
    browser.getControl('person').displayValue = ['Unstable, Urs']
    browser.getControl('password', index=0).value = '09876543'
    browser.getControl('password', index=1).value = '09876543'
    browser.getControl('Add').click()
    assert '"Unstable, Urs" added.' == browser.message


def test_principals__EditForm__1(localadmin, address_book, UserFactory):
    """`EditForm` allows to edit a principal."""
    UserFactory(address_book, 'Hans', 'Tester', 'hans@example.com',
                '1234567890', ['Archive Visitor'])
    browser = localadmin.open(localadmin.PRINCIPALS_LIST_URL)
    browser.getLink('Tester, Hans').click()
    assert browser.PRINCIPAL_EDIT_URL == browser.url
    assert 'hans@example.com' == browser.getControl('login').value
    # The password is not displayed.
    assert '' == browser.getControl('password', index=0).value
    assert '' == browser.getControl('password repetition').value
    assert browser.getControl('Archive Visitor').selected
    browser.getControl('notes').value = 'Hans the tester'
    browser.getControl('login').value = 'hans@example.com'
    browser.getControl('roles').displayValue = ['Editor']
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.PRINCIPALS_LIST_URL == browser.url
    assert 'Hans the tester' in browser.contents
    browser.open(browser.PRINCIPAL_EDIT_URL)
    assert 'Hans the tester' == browser.getControl('notes').value
    assert 'hans@example.com' == browser.getControl('login').value
    assert ['Editor'] == browser.getControl('roles').displayValue


def test_principals__EditForm__2(localadmin, address_book, UserFactory):
    """`EditForm` allows to cancel editing."""
    UserFactory(address_book, 'Hans', 'Tester', 'hans@example.com',
                '1234567890', ['Visitor'])
    browser = localadmin.open(localadmin.PRINCIPAL_EDIT_URL)
    browser.getControl('notes').value = '2nd new visitor'
    browser.getControl('Cancel').click()
    assert 'No changes were applied.' == browser.message
    assert browser.PRINCIPALS_LIST_URL == browser.url
    assert '2nd new visitor' not in browser.contents


def test_principals__EditForm__3(localadmin, address_book, UserFactory):
    """`EditForm` makes sure the login name of the principals stays unique."""
    UserFactory(address_book, 'Hans', 'Tester', 'hans@example.com',
                '1234567890', ['Visitor'])
    browser = localadmin.open(localadmin.PRINCIPAL_EDIT_URL)
    browser.getControl('login').value = 'arne@example.com'
    browser.getControl('Save').click()
    assert [] == browser.message
    assert (['Principal Login already taken!'] ==
            browser.etree.xpath('//div[@class="error"]/text()'))


def test_principals__EditForm__4(localadmin):
    """Changing the mail address in persons data does change the login name."""
    browser = localadmin.open(localadmin.PERSON_EDIT_URL)
    browser.getControl('e-mail address', index=1).value = 'htester@example.com'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    browser.open(browser.PRINCIPAL_EDIT_URL_1)
    assert 'arne@example.com' == browser.getControl('login').value


def test_principals__EditForm__5(address_book, UserFactory, browser):
    """A visitor can only change his password in the `EditForm`."""
    UserFactory(address_book, u'Urs', u'Unstable', u'uu@example.com',
                'u1u2u3u4', ['Visitor'])
    browser.formlogin(u'uu@example.com', 'u1u2u3u4')
    browser.open(browser.PRINCIPAL_EDIT_URL_1)
    # There are only the password fields and submit controls, but there is no
    # delete button:
    assert ['form.buttons.apply',
            'form.buttons.cancel',
            'form.widgets.password',
            'form.widgets.password_repetition'] == browser.all_control_names
    browser.getControl('password', index=0).value = 'new_password'
    browser.getControl('password repetition').value = 'new_password'
    browser.getControl('Save').click()
    # Changing the password immediately asks the visitor for his new
    # credentials:
    assert (
        ['You changed the password, please re-login.',
         'Data successfully updated.',
         'To log-in enter your username and password and submit the form.'] ==
        browser.message)
    assert browser.url.startswith(browser.LOGIN_BASE_URL)
    browser.formlogin(u'uu@example.com', 'new_password', use_current_url=True)
    # The new password can also be used to "normally" log-in:
    browser.logout()
    browser.formlogin('uu@example.com', 'new_password', use_current_url=True)
    assert browser.url.startswith(browser.PRINCIPALS_LIST_URL)  # +/index.html


def test_principals__EditForm__5_5(address_book, UserFactory, browser):
    """If a visitor does not change his password, he is not logged out."""
    UserFactory(address_book, u'Urs', u'Unstable', u'uu@example.com',
                'u1u2u3u4', ['Visitor'])
    browser.formlogin(u'uu@example.com', 'u1u2u3u4')
    browser.open(browser.PRINCIPAL_EDIT_URL_1)
    browser.getControl('Save').click()
    # Changing the password immediately asks the visitor for his new
    # credentials:
    assert 'Data successfully updated.' == browser.message
    assert browser.PRINCIPALS_LIST_URL == browser.url


@pytest.mark.parametrize('role', ('Editor', 'Archivist'))
def test_principals__EditForm__6(address_book, UserFactory, browser, role):
    """An editor can edit his own user data but not the roles."""
    user = UserFactory(address_book, u'Urs', u'Unstable', u'uu@example.com',
                       'u1u2u3u4', [role])
    user.description = u'Hans the tester'
    browser.formlogin(u'uu@example.com', 'u1u2u3u4')
    browser.open(browser.PRINCIPAL_EDIT_URL_1)
    # There are all fields besides the roles field and the submit controls,
    # but there is no delete button:
    assert ['form.buttons.apply',
            'form.buttons.cancel',
            'form.widgets.description',
            'form.widgets.login',
            'form.widgets.password',
            'form.widgets.password_repetition'] == browser.all_control_names
    assert 'uu@example.com' == browser.getControl('login').value
    assert '' == browser.getControl('password', index=0).value
    assert 'Hans the tester' == browser.getControl('notes').value
    # The editor can change the data and save them. The login-name needn't
    # even be an e-mail address. Changing the own log-in name immediately
    # asks the user for his new credentials:
    browser.getControl('login').value = 'hans.tester'
    browser.getControl('password', index=0).value = 'testtest'
    browser.getControl('password repetition').value = 'testtest'
    browser.getControl('notes').value = 'The big HANS'
    browser.getControl('Save').click()
    assert (
        ['You changed the login name, please re-login.',
         'You changed the password, please re-login.',
         'Data successfully updated.',
         'To log-in enter your username and password and submit the form.'] ==
        browser.message)
    assert browser.url.startswith(browser.LOGIN_BASE_URL)
    browser.formlogin('hans.tester', 'testtest', use_current_url=True)
    assert browser.url.startswith(browser.PRINCIPALS_LIST_URL)  # +/index.html
    # The data was stored:
    browser.getLink('Unstable').click()
    assert 'hans.tester' == browser.getControl('login').value
    assert '' == browser.getControl('password', index=0).value
    assert 'The big HANS' == browser.getControl('notes').value
    # The new log-in name an password can also be used to "normally" log-in:
    browser.logout()
    browser.formlogin('hans.tester', 'testtest', use_current_url=True)
    assert browser.url.startswith(browser.PRINCIPAL_EDIT_URL_1)  # +/index.html


def test_principals__EditForm__7(
        address_book, UserFactory, localadmin, browser2):
    """Changing roles in `EditForm` changes the permissions of the user."""
    UserFactory(address_book, u'Urs', u'Unstable', u'uu@example.com',
                'u1u2u3u4', ['Visitor'])
    # As a visitor the user not able to create new persons:
    browser = browser2.formlogin(u'uu@example.com', 'u1u2u3u4')
    browser.assert_forbidden(browser.PERSON_ADD_URL)
    # When the administrator changes the roles of a user ...
    localadmin.open(localadmin.PRINCIPAL_EDIT_URL)
    localadmin.getControl('roles').displayValue = ['Editor']
    localadmin.getControl('Save').click()
    assert 'Data successfully updated.' == localadmin.message
    assert localadmin.PRINCIPALS_LIST_URL == localadmin.url
    # ... he immediately gets the new permissions:
    browser.open(browser.PERSON_ADD_URL)
    assert browser.getControl('first name')


def test_principals__EditForm__8(
        address_book, UserFactory, localadmin, browser2, browser3):
    """Removing all roles from a user only allows him to access following tabs:

    * master data.
    * about

    He can see an empty users listing.
    """
    UserFactory(address_book, u'Urs', u'Unstable', u'uu@example.com',
                'u1u2u3u4', ['Visitor'])
    browser = browser2.formlogin(u'uu@example.com', 'u1u2u3u4')
    # When the administrator removes all roles from a user ...
    browser.reload()
    url = browser.url
    localadmin.open(localadmin.PRINCIPAL_EDIT_URL)
    localadmin.getControl('roles').displayValue = []
    localadmin.getControl('Save').click()
    assert 'Data successfully updated.' == localadmin.message
    assert localadmin.PRINCIPALS_LIST_URL == localadmin.url

    browser.open(url)
    assert [
        'Master data',
        'About',
    ] == browser.etree.xpath(
        '//div[@class="menuToggle main-menu"]/ul/li/a/span/text()')
    browser.getLink('Master data').click()

    assert ['Users'] == browser.etree.xpath(
        '//ul[@class="bullet"]/li/a/span/child::text()')
    browser.getLink('Users').click()
    assert ('No users defined yet or you are not allowed to access any.'
            in browser.contents)


def test_principals__DeleteUserForm__1(address_book, UserFactory, localadmin):
    """`DeleteUserForm` allows an administrator to delete a user."""
    UserFactory(address_book, u'Urs', u'Unstable', u'uu@example.com',
                'u1u2u3u4', ['Visitor'])
    browser = localadmin.open(localadmin.PRINCIPAL_EDIT_URL)
    browser.getControl('Delete user').click()
    assert browser.PRINCIPAL_DELETE_URL == browser.url
    browser.getControl('Yes').click()
    assert '"Unstable, Urs" deleted.' == browser.message
    assert browser.PRINCIPALS_LIST_URL == browser.url
    assert ['Admin, Arne'] == browser.etree.xpath('//td/a/text()')


def test_principals__DeleteUserForm__2(address_book, UserFactory, localadmin):
    """`DeleteUserForm` allows to cancel deletion of a user."""
    UserFactory(address_book, u'Urs', u'Unstable', u'uu@example.com',
                'u1u2u3u4', ['Visitor'])
    browser = localadmin.open(localadmin.PRINCIPAL_DELETE_URL)
    browser.getControl('No, cancel').click()
    assert 'Deletion canceled.' == browser.message
    assert browser.PRINCIPAL_EDIT_URL == browser.url


@pytest.mark.parametrize('username', ['visitor', 'editor', 'archivist'])
def test_principals__DeleteUserForm__3(
        address_book, UserFactory, browser, username):
    """Non-Admin users cannot access `DeleteUserForm`."""
    UserFactory(address_book, u'Urs', u'Unstable', u'uu@example.com',
                'u1u2u3u4', ['Visitor'])
    browser.login(username)
    browser.assert_forbidden(browser.PRINCIPAL_DELETE_URL_1)

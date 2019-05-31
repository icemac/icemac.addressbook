import pytest


def test_session__FlashedSessionCredentialsPlugin__1(address_book, browser):
    """The login screen displays a flash message.

    As cookie authorization is used an unauthorized user is redirected to
    the log-in page.

    """
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    assert (
        'To log-in enter your username and password and submit the form.' ==
        browser.message)
    assert (
        browser.LOGIN_BASE_URL +
        '%3A%2F%2Flocalhost%2Fab%2F%40%40index.html' == browser.url)


@pytest.mark.parametrize('username, password',
                         (('wrong_username@example.com', '123456789'),
                          ('username@example.com', 'wrong_123456789')))
def test_session__FlashedSessionCredentialsLoginForm__1(
        address_book, UserFactory, browser, username, password):
    """A wrong user name or password at login leads to an error message.

    No time-stamp of this attempt is stored.
    """
    user = UserFactory(address_book, u'Test', u'User', u'username@example.com',
                       u'123456789', ['Visitor'])
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    browser.getControl('User Name').value = username
    browser.getControl('Password').value = password
    browser.getControl('Log in').click()
    assert ('Login failed. Username and/or password might be wrong.' ==
            browser.message)
    assert 'Please provide Login Information' in browser.contents
    assert (
        browser.LOGIN_BASE_URL +
        '%3A%2F%2Flocalhost%2Fab%2F%40%40index.html' == browser.url)
    assert user.last_login is None
    # User name and password are not re-displayed if there was an error:
    assert '' == browser.getControl('User Name').value
    assert '' == browser.getControl('Password').value


@pytest.mark.parametrize('role', ('Visitor', 'Editor', 'Administrator'))
def test_session__FlashedSessionCredentialsLoginForm__2(
        address_book, UserFactory, DateTime, browser, role):
    """A user is able to log-in using the cookie login form.

    His last log-in timestamp is stored.
    """
    user = UserFactory(address_book, u'Test', u'User', u'username@example.com',
                       u'123456789', [role])
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    browser.getControl('User Name').value = 'username@example.com'
    browser.getControl('Password').value = '123456789'
    browser.getControl('Log in').click()
    assert 'You have been logged-in successfully.' == browser.message
    assert browser.ADDRESS_BOOK_WELCOME_URL == browser.url
    assert user.last_login is not None
    assert DateTime.add(DateTime.now, seconds=-5) < user.last_login
    browser.getLink('Master data').click()
    browser.getLink('Users').click()
    # Role name and last log-in are shown in user list:
    assert (
        '<td>username@example.com</td><td>{}</td><td>{}</td>'.format(
            role, DateTime.format(user.last_login).replace(' ', '')) in
        browser.contents_without_whitespace)


@pytest.mark.parametrize('role', ('Visitor', 'Editor', 'Administrator'))
def test_session__FlashedSessionCredentialsLoginForm__3(
        address_book, UserFactory, browser, role):
    """Selecting the ``Logout``-Link leads to the log-in form."""
    UserFactory(address_book, u'Test', u'User', u'username@example.com',
                u'123456789', [role])
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    browser.getControl('User Name').value = 'username@example.com'
    browser.getControl('Password').value = '123456789'
    browser.getControl('Log in').click()
    # Logout:
    browser.logout()
    assert (
        ['You have been logged out successfully.',
         'To log-in enter your username and password and submit the form.'] ==
        browser.message)
    assert (
        browser.LOGIN_BASE_URL +
        '%3A%2F%2Flocalhost%2Fab%2F%40%40welcome.html' == browser.url)


def test_session__FlashedSessionCredentialsLoginForm__4(
        address_book, AddressBookFactory, UserFactory, browser):
    """Log-in to another address book not possible.

    It is not possible to log in into another address book besides the one
    the user was created in (password does not get accepted).

    """
    UserFactory(address_book, u'Ad', u'Min', u'admin@example.com',
                u'123456789', ['Administrator'])
    AddressBookFactory('ab2')
    browser.open('http://localhost/ab2')
    assert ('http://localhost/ab2/@@loginForm.html?camefrom='
            'http%3A%2F%2Flocalhost%2Fab2%2F%40%40index.html' == browser.url)
    browser.getControl('User Name').value = 'admin@example.com'
    browser.getControl('Password').value = '123456789'
    browser.getControl('Log in').click()
    assert ('Login failed. Username and/or password might be wrong.' ==
            browser.message)
    assert ('http://localhost/ab2/@@loginForm.html?camefrom='
            'http%3A%2F%2Flocalhost%2Fab2%2F%40%40index.html' == browser.url)

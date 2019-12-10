from zope.testbrowser.browser import LinkNotFoundError
import pytest


@pytest.mark.webdriver
def test_crud__AddForm__1_webdriver(address_book, webdriver):
    """A new address book can be added and edited."""
    ab = webdriver.address_book
    # Only managers are allowed to create address books:
    webdriver.login('globalmgr', ab.ROOT_URL)
    ab.create()
    ab.title = 'test book'
    ab.assert_default_favicon_selected()
    ab.select_favicon(1)
    ab.timezone = 'Europe/Berlin'
    ab.submit('add')
    assert webdriver.message == '"test book" added.'
    assert ab.ADDRESS_BOOK_2_WELCOME_URL == webdriver.path
    # Editing is done in master data section:
    webdriver.open(ab.ADDRESS_BOOK_EDIT_URL.replace('/ab', '/AddressBook'))
    # The add form actually stored the values:
    assert 'test book' == ab.title
    ab.assert_favicon_selected(1)
    assert "Europe/Berlin" == ab.timezone
    # The edit form is able to change the data:
    ab.title = 'ftest book'
    ab.select_favicon(0)
    ab.submit('apply')
    assert 'Data successfully updated.' == webdriver.message
    # The edit form submits to itself and shows the stored data:
    assert ab.title == 'ftest book'
    ab.assert_favicon_selected(0)
    # The selected time zone shows up in user's preferences:
    prefs = webdriver.prefs
    webdriver.open(prefs.PREFS_URL.replace('/ab', '/AddressBook', 1))
    prefs.open_time_zone_element()
    assert "Europe/Berlin" == prefs.timezone


def test_crud__AddForm__2(address_book, browser):
    """A new address book can be added."""
    browser.login('globalmgr')
    browser.open(browser.ROOT_URL)
    browser.getLink('address book').click()
    assert browser.ADDRESS_BOOK_ADD_URL == browser.url
    browser.getControl('title').value = 'test 2'
    browser.select_favicon()
    browser.getControl('Time zone').displayValue = ['Africa/Juba']
    browser.getControl('Add').click()
    assert '"test 2" added.' == browser.message
    assert browser.ADDRESS_BOOK_2_WELCOME_URL == browser.url


def test_crud__EditForm__1(address_book, browser):
    """An address book can be edited."""
    browser.login('mgr')
    browser.open(browser.ADDRESS_BOOK_EDIT_URL)
    browser.select_favicon()
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message


def test_crud__EditForm__2(address_book, browser):
    """Editing the addressbook can be canceled."""
    address_book.title = u'ftest-ab'
    browser.login('mgr')
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    browser.getLink('Master data').click()
    browser.getLink('Address book').click()
    assert browser.ADDRESS_BOOK_EDIT_URL == browser.url
    assert 'ftest-ab' == browser.getControl('title').value
    browser.getControl('title').value = 'fancy book'
    browser.getControl('Cancel').click()
    assert 'No changes were applied.' == browser.message
    assert 'ftest-ab' == browser.getControl('title').value


@pytest.mark.parametrize("loginname", ('editor', 'visitor', 'archivist'))
def test_crud__EditForm__3(address_book, browser, loginname):
    """Some roles are not allowed to edit address book's data."""
    # There is no link to edit the address book's data (title) because
    # the user is not allowed to do so:
    browser.login(loginname)
    browser.open(browser.MASTER_DATA_URL)
    with pytest.raises(LinkNotFoundError):
        browser.getLink('Address book')
    # Even opening the URL is not possible:
    browser.assert_forbidden(browser.ADDRESS_BOOK_EDIT_URL)


def test_crud__DeleteContentForm__1(
        address_book, PersonFactory, UserFactory, PostalAddressFactory,
        browser):
    """The Administrator is able to delete all persons in the address book."""
    # Make sure there are some persons (with addresses) and some users
    # in the address book:
    PersonFactory(address_book, last_name=u'Tester')
    PersonFactory(address_book, last_name=u'Tester 2')
    UserFactory(
        address_book, u'Hans', u'User', u'hans@user.de', u'asdf', ['Visitor'])
    UserFactory(
        address_book, u'Kurt', u'Utzr', u'kurt@utzr.ch', u'asdf', ['Editor'])
    t3 = PersonFactory(address_book, last_name=u'Tester 3')
    PostalAddressFactory(t3, city=u'Hettstedt')

    # To delete all persons in the address book, the Adminstrator has to
    # open the `edit address book` form and select the `Delete all
    # persons in address book` button there. An `are you sure` form is
    # displayed:
    browser.login('mgr')
    browser.open(browser.ADDRESS_BOOK_EDIT_URL)
    browser.getControl('Delete all persons in address book').click()
    assert browser.ADDRESS_BOOK_DELETE_PERSONS_URL == browser.url
    assert ('Do you really want to delete all persons in this address book?' in
            browser.contents)
    # The number of persons in the address book is displayed:
    assert 'class="text-widget int-field">5</span>' in browser.contents
    browser.getControl('Yes').click()
    assert 'Address book contents deleted.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    # Users are not deleted because the are referenced as a safety belt so the
    # current user does not delete his credentials.
    assert 'Person-3">User' in browser.contents
    assert 'Person-4">Utzr' in browser.contents


def test_crud__DeleteContentForm__2(address_book, PersonFactory, browser):
    """`DeleteContentForm` allows to cancel delete."""
    PersonFactory(address_book, last_name=u'Tester')
    browser.login('mgr')
    browser.open(browser.ADDRESS_BOOK_DELETE_PERSONS_URL)
    browser.getControl('No, cancel').click()
    assert 'Deletion canceled.' == browser.message
    assert browser.ADDRESS_BOOK_EDIT_URL == browser.url


@pytest.mark.parametrize("loginname", ('editor', 'visitor', 'archivist'))
def test_crud__DeleteContentForm__3(address_book, browser, loginname):
    """Some roles are not allowed to delete all persons in address book."""
    browser.login(loginname)
    browser.assert_forbidden(browser.ADDRESS_BOOK_DELETE_PERSONS_URL)


def test_crud__DeleteForm__1(address_book, UserFactory, browser):
    """`DeleteForm` allows Administrator to delete the whole addressbook."""
    # Users are a bit harder to delete, so we add them to show they can get
    # deleted as well:
    UserFactory(address_book, u'B.', u'Ude', u'b@u.de', u'asdf', ['Visitor'])
    UserFactory(address_book, u'B.', u'Uch', u'b@u.ch', u'asdf', ['Editor'])
    browser.login('globalmgr')
    browser.open(browser.ROOT_URL)
    browser.getLink('Delete').click()
    assert browser.ADDRESS_BOOK_DELETE_URL == browser.url
    browser.getControl('Yes').click()
    assert '"test addressbook" deleted.' == browser.message
    assert browser.ROOT_URL_WITHOUT_SLASH == browser.url
    assert 'There are no address books' in browser.contents


def test_crud__DeleteForm__2(address_book, UserFactory, browser):
    """`DeleteForm` can be canceled."""
    browser.login('mgr')
    browser.open(browser.ADDRESS_BOOK_DELETE_URL)
    browser.getControl('No, cancel').click()
    assert 'Deletion canceled.' == browser.message
    assert browser.ROOT_URL_WITHOUT_SLASH == browser.url


@pytest.mark.parametrize('user', ['visitor', 'editor', 'archivist'])
def test_crud__DeleteForm__3(address_book, browser, user):
    """Non-admin users are not able to access `DeleteForm`."""
    browser.login(user)
    browser.assert_forbidden(browser.ADDRESS_BOOK_DELETE_URL)


def test_crud__welcome_pt__1(address_book, browser):
    """The greeting displayed after login contains the address book title."""
    address_book.title = u'ftest-ab'
    browser.login('visitor')
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    assert '<p>Welcome to ftest-ab.</p>'in browser.contents

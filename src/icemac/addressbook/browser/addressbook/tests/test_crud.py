from mechanize import HTTPError
import pytest


@pytest.mark.webdriver
def test_crud__AddForm__1(address_book, webdriver):
    """A new address book can be added and edited."""
    # Only managers are allowed to create address books:
    sel = webdriver.login('globalmgr')
    # On the start page there is a link to add an address book:
    sel.clickAndWait('link=address book')
    sel.type('id=form-widgets-title', 'test book')

    # Default value of favicon is pre-selected:
    sel.assertCssCount(
        'css=.ui-selected '
        'img[src="/++resource++img/favicon-red-preview.png"]', 1)
    sel.clickAt('form-widgets-favicon-1', '20,20')
    # Default time zone can be selected:
    sel.select("id=form-widgets-time_zone", "label=Europe/Berlin")
    sel.clickAndWait('form-buttons-add')
    assert webdriver.message == '"test book" added.'
    sel.assertLocation('http://%s/AddressBook/@@welcome.html' % sel.server)
    # Editing is done in master data section:
    sel.clickAndWait('link=Master data')
    sel.clickAndWait('link=Address book')
    assert sel.getLocation().endswith('/AddressBook/@@edit-address_book.html')
    # The add form actually stored the values:
    sel.assertValue('id=form-widgets-title', 'test book')
    sel.assertCssCount('css=#form-widgets-favicon-1.ui-selected', 1)
    sel.assertSelectedLabel("id=form-widgets-time_zone", "Europe/Berlin")
    # The edit form is able to change the data:
    sel.clear('id=form-widgets-title')
    sel.type('id=form-widgets-title', 'ftest book')
    sel.clickAt('form-widgets-favicon-0', '20,20')
    sel.clickAndWait('form-buttons-apply')
    assert 'Data successfully updated.' == webdriver.message
    # The edit form submits to itself and shows the stored data:
    sel.assertValue('id=form-widgets-title', 'ftest book')
    sel.assertCssCount('css=#form-widgets-favicon-0.ui-selected', 1)
    # The selected time zone shows up in user's preferences:
    sel.clickAndWait("link=Preferences")
    sel.click("css=fieldset.timeZone")
    sel.waitForElementPresent("id=form-widgets-time_zone")
    sel.assertSelectedLabel("id=form-widgets-time_zone", "Europe/Berlin")


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


@pytest.mark.parametrize("loginname", ('editor', 'visitor'))
def test_crud__EditForm__3(address_book, browser, loginname):
    """Some roles are not allowed to edit address book's data."""
    from mechanize import LinkNotFoundError, HTTPError
    # There is no link to edit the address book's data (title) because
    # the user is not allowed to do so:
    browser.login(loginname)
    browser.open(browser.MASTER_DATA_URL)
    with pytest.raises(LinkNotFoundError):
        browser.getLink('Address book')
    # Even opening the URL is not possible:
    with pytest.raises(HTTPError) as err:
        browser.open(browser.ADDRESS_BOOK_EDIT_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)


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


@pytest.mark.parametrize("loginname", ('editor', 'visitor'))
def test_crud__DeleteContentForm__3(address_book, browser, loginname):
    """Some roles are not allowed to delete all persons in address book."""
    browser.login(loginname)
    with pytest.raises(HTTPError) as err:
        browser.open(browser.ADDRESS_BOOK_DELETE_PERSONS_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)


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
    assert browser.ROOT_URL == browser.url
    assert 'There are no address books' in browser.contents


def test_crud__DeleteForm__2(address_book, UserFactory, browser):
    """`DeleteForm` can be canceled."""
    browser.login('mgr')
    browser.open(browser.ADDRESS_BOOK_DELETE_URL)
    browser.getControl('No, cancel').click()
    assert 'Deletion canceled.' == browser.message
    assert browser.ROOT_URL == browser.url


@pytest.mark.parametrize('user', ['visitor', 'editor'])
def test_crud__DeleteForm__3(address_book, browser, user):
    """Non-admin users are not able to access `DeleteForm`."""
    browser.login(user)
    with pytest.raises(HTTPError) as err:
        browser.open(browser.ADDRESS_BOOK_DELETE_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)


def test_crud__welcome_pt__1(address_book, browser):
    """The greeting displayed after login contains the address book title."""
    address_book.title = u'ftest-ab'
    browser.login('visitor')
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    assert ('<p>Welcome to ftest-ab. Please select one of the tabs above.</p>'
            in browser.contents)

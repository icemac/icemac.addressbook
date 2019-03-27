import pytest


def test_keyword__Table__1(address_book, browser):
    """The `Table` shows that initially no keywords are defined."""
    browser.login('editor')
    browser.open(browser.MASTER_DATA_URL)
    browser.getLink('Keywords').click()
    assert browser.KEYWORDS_LIST_URL == browser.url
    assert '>No keywords defined yet.<' in browser.contents


def test_keyword__Table__2(address_book, KeywordFactory, browser):
    """The `Table` shows keywords case insensitive alphabetically sorted."""
    KeywordFactory(address_book, u'Company co-worker')
    KeywordFactory(address_book, u'church')
    KeywordFactory(address_book, u'friend')
    KeywordFactory(address_book, u'family')
    browser.login('editor')
    browser.open(browser.KEYWORDS_LIST_URL)
    assert ['church',
            'Company co-worker',
            'family',
            'friend'] == browser.etree.xpath('//tr/td/a/text()')


def test_keyword__Table__3(address_book, KeywordFactory, browser):
    """A visitor is allowed to see the keywords in the `Table`."""
    KeywordFactory(address_book, u'Arbeit')
    browser.login('visitor')
    browser.open(browser.KEYWORDS_LIST_URL)
    assert ['Arbeit'] == browser.etree.xpath('//tbody/tr/td/a/text()')


def test_keyword__AddForm__1(address_book, browser):
    """The `AddForm` allows to add a new keyword."""
    browser.login('editor')
    browser.open(browser.KEYWORDS_LIST_URL)
    browser.getLink('keyword').click()
    assert browser.KEYWORD_ADD_URL == browser.url
    browser.getControl('keyword').value = 'company coworkr'
    browser.getControl('Add').click()
    assert '"company coworkr" added.' == browser.message


def test_keyword__AddForm__2(address_book, KeywordFactory, browser):
    """`AddForm` prevents from creating duplicate keyword titles."""
    KeywordFactory(address_book, u'Kirche')
    browser.login('editor')
    browser.open(browser.KEYWORD_ADD_URL)
    browser.getControl('keyword').value = 'Kirche'
    browser.getControl('Add').click()
    assert [] == browser.message
    assert browser.KEYWORD_ADD_URL == browser.url
    assert ['This keyword already exists.'] == browser.etree.xpath(
        '/descendant-or-self::div[@class="error"]/text()')


def test_keyword__EditForm__1(address_book, KeywordFactory, browser):
    """The `EditForm` allows to edit the keyword."""
    KeywordFactory(address_book, u'company coworkr')
    browser.login('editor')
    browser.open(browser.KEYWORDS_LIST_URL)
    browser.getLink('company coworkr').click()
    assert browser.KEYWORD_EDIT_URL == browser.url
    assert 'company coworkr' == browser.getControl('keyword').value
    # The last modification date is also displayed:
    assert '<legend>metadata</legend>' in browser.contents
    assert '<span>Modification Date (UTC)</span>' in browser.contents
    # We correct the typo to show the edit form works:
    browser.getControl('keyword').value = 'Company co-worker'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    # To show that the changes where saved we go again to the form:
    browser.getLink('Company co-worker').click()
    assert 'Company co-worker' == browser.getControl('keyword').value


def test_keyword__EditForm__2(address_book, KeywordFactory, browser):
    """The user can cancel changes he made in the `EditForm`."""
    KeywordFactory(address_book, u'Company co-worker')
    browser.login('editor')
    browser.open(browser.KEYWORD_EDIT_URL)
    browser.getControl('keyword').value = 'typo'
    browser.getControl('Cancel').click()
    assert 'No changes were applied.' == browser.message
    # The value really did not change:
    browser.getLink('Company co-worker').click()
    assert 'Company co-worker' == browser.getControl('keyword').value


def test_keyword__EditForm__3(
        address_book, KeywordFactory, FullPersonFactory, browser):
    """Changing a keyword in `EditForm` changes the keyword at the person."""
    family = KeywordFactory(address_book, u'family')
    KeywordFactory(address_book, u'church')
    FullPersonFactory(address_book, u'Tester', keywords=set([family]))
    browser.login('editor')
    browser.open(browser.KEYWORD_EDIT_URL)
    browser.getControl('keyword').value = 'Familie'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message

    browser.getLink('church').click()
    browser.getControl('keyword').value = 'Kirche'
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message

    browser.getLink('Person list').click()
    browser.getLink('Tester').click()
    assert browser.getControl('Familie').selected
    assert not browser.getControl('Kirche').selected
    with pytest.raises(LookupError) as err:
        browser.getControl('church')
    assert str(err.value).startswith("label 'church'")


def test_keyword__EditForm__4(
        address_book, KeywordFactory, FullPersonFactory, browser):
    """`EditForm` does not display a delete button for a referenced keyword."""
    FullPersonFactory(address_book, u'Tester',
                      keywords=set([KeywordFactory(address_book, u'keyword')]))
    browser.login('editor')
    browser.open(browser.KEYWORD_EDIT_URL)
    assert ['form.buttons.apply',
            'form.buttons.cancel'] == browser.submit_control_names


def test_keyword__EditForm__5(
        address_book, KeywordFactory, FullPersonFactory, browser):
    """`EditForm` prevents from duplicate keyword titles."""
    # Modifying the title of a keyword so that it is equal to another one
    # leads also to an error message (We create a new keyword first and edit
    # it afterwards.):
    KeywordFactory(address_book, u'Arbeit')
    KeywordFactory(address_book, u'Company co-worker')
    browser.login('editor')
    browser.open(browser.KEYWORD_EDIT_URL)
    browser.getControl('keyword').value = 'Company co-worker'
    browser.getControl('Save').click()
    assert [] == browser.message
    assert browser.KEYWORD_EDIT_URL
    assert ['This keyword already exists.'] == browser.etree.xpath(
        '/descendant-or-self::div[@class="error"]/text()')


def test_keyword__EditForm__6(address_book, KeywordFactory, browser):
    """A visitor does not see any form fields in the `EditForm`."""
    KeywordFactory(address_book, u'Arbeit')
    browser.login('visitor')
    browser.open(browser.KEYWORD_EDIT_URL)
    # There is no delete button, too:
    assert ['form.buttons.apply',
            'form.buttons.cancel'] == browser.all_control_names


def test_keyword__DeleteForm__1(address_book, KeywordFactory, browser):
    """Deletion can be canceled in the `DeleteForm`."""
    KeywordFactory(address_book, u'friend')
    browser.login('editor')
    browser.open(browser.KEYWORD_EDIT_URL)
    browser.getControl('Delete').click()
    # There is a confirmation dialog where the user has to decide if he
    # really wants to delete the keyword. If he decides not to delete the
    # entry he is led back to the keyword's edit form:
    assert browser.KEYWORD_DELETE_URL == browser.url
    browser.getControl('No, cancel').click()
    assert 'Deletion canceled.' == browser.message
    assert browser.KEYWORD_EDIT_URL == browser.url


def test_keyword__DeleteForm__2(address_book, KeywordFactory, browser):
    """Deletion can be confirmed in the `DeleteForm`."""
    KeywordFactory(address_book, u'friend')
    browser.login('editor')
    browser.open(browser.KEYWORD_EDIT_URL)
    # Submit buttons when the keyword can be deleted:
    assert ['form.buttons.apply',
            'form.buttons.cancel',
            'form.buttons.delete'] == browser.submit_control_names
    # If he decides to delete the entry he is led back to the keyword list
    # where the keyword is no longer listed:
    browser.getControl('Delete').click()
    browser.getControl('Yes').click()
    assert '"friend" deleted.' == browser.message
    assert browser.KEYWORDS_LIST_URL == browser.url
    # Get rid of the message containing "friend":
    browser.open(browser.KEYWORDS_LIST_URL)
    assert 'friend' not in browser.contents


def test_keyword__DeleteForm__3(
        address_book, KeywordFactory, FullPersonFactory, browser):
    """Deletion of a referenced leads to IntegrityError in the `DeleteForm`."""
    from gocept.reference.interfaces import IntegrityError
    FullPersonFactory(address_book, u'Tester',
                      keywords=set([KeywordFactory(address_book, u'keyword')]))
    browser.login('editor')
    browser.open(browser.KEYWORD_DELETE_URL)
    browser.handleErrors = False  # neded for nicer error display below
    with pytest.raises(IntegrityError) as err:
        browser.getControl('Yes').click()
    assert str(err.value).startswith("Can't delete or move")
    assert str(err.value).endswith("is still being referenced.")


@pytest.mark.parametrize('loginname', ['visitor', 'archivist'])
def test_keyword__DeleteForm__4(
        address_book, KeywordFactory, browser, loginname):
    """It cannot be opened by some roles even knowing the URL."""
    KeywordFactory(address_book, u'work')
    browser.login('visitor')
    browser.assert_forbidden(browser.KEYWORD_DELETE_URL)

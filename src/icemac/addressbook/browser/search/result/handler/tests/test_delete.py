from zope.testbrowser.browser import HTTPError
import pytest


def test_delete__DeleteForm__1(search_data, UserFactory, browser):
    """`DeleteForm` allows an administrator to delete found persons."""
    address_book = search_data
    # Create a user -- the person of a user cannot be deleted using this search
    # result handler.
    UserFactory(address_book, u'Ben', u'Utzer', u'ben@example.com',
                u'12345678', [], keywords=[u'church'])
    browser.login('mgr')
    browser.keyword_search('church')
    # Only the selected persons get deleted. Deselected persons will not:
    browser.getControl(name='persons:list').getControl(
        value="Person-2").selected = False  # This this the person named "Koch"
    browser.getControl('Apply on selected persons').displayValue = [
        'Delete']
    browser.getControl(name='form.buttons.apply').click()
    # The number of persons for deletion is shown on the question screen:
    # (There are 3 persons with the church keyword in the fixture, one got
    # deselected but there is additionally a newly created user.
    assert ['3'] == browser.etree.xpath(
        '//span[@id="form-widgets-count"]/text()')
    assert browser.SEARCH_DELETE_URL == browser.url
    browser.getControl('Yes').click()
    assert 'Selected persons deleted: 2' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    # Only the two non-users got deleted:
    assert 'Koch' in browser.contents
    assert 'Utzer' in browser.contents
    assert 'Liebig' not in browser.contents
    assert 'Velleuer' not in browser.contents


def test_delete__DeleteForm__2(search_data, browser):
    """`DeleteForm` can be canceled."""
    browser.login('mgr')
    browser.keyword_search('church', 'Delete')
    # Seleting the `cancel` button leads to the person list without deleting
    # anybody:
    browser.getControl('No, cancel').click()
    assert 'Deletion canceled.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    assert 'Koch' in browser.contents
    assert 'Liebig' in browser.contents
    assert 'Velleuer' in browser.contents


@pytest.mark.parametrize('role', ['editor', 'visitor'])
def test_delete__DeleteForm__3(search_data, browser, role):
    """`DeleteForm` cannot be accessed by non-admin users."""
    browser.login(role)
    browser.keyword_search('church')
    # There is no delete option which can be applied:
    assert (
        ['XLS export main (Exports person data and main addresses resp. '
         'phone numbers.)',
         'XLS export complete (Exports person data and all addresses resp. '
         'phone numbers.)',
         'E-Mail (Creates a link to send e-mails.)',
         'Names (Comma separated list of person names.)',
         'Checklist (List of person names with check-boxes.)',
         "iCalendar export birthday (Export person's birthdays as "
         ".ics file.)"] ==
        browser.getControl('Apply on selected persons').displayOptions)
    with pytest.raises(HTTPError) as err:
        browser.open(browser.SEARCH_DELETE_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)

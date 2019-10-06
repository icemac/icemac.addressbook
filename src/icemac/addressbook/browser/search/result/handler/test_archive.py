import pytest


search_result_handlers_without_archive_for_editor = [
    'XLS export main (Exports person data and main addresses resp. '
    'phone numbers.)',
    'XLS export complete (Exports person data and all addresses resp. '
    'phone numbers.)',
    'E-Mail (Creates a link to send e-mails.)',
    'Names (Comma separated list of person names.)',
    'Checklist (List of person names with check-boxes.)',
    'iCalendar export birthday (Export person\'s birthdays as .ics file.)',
    'Birthday list (Person names sorted by birthday.)',
]

search_result_handlers_without_archive_for_mgr = \
    search_result_handlers_without_archive_for_editor + [
        'Update (Allows you to choose a field for update on each selected'
        ' person.)',
        'Deletion (Deletes selected persons.)'
    ]


def test_archive__ArchiveForm__1(search_data, UserFactory, browser):
    """It allows an administrator to archive found persons."""
    address_book = search_data
    # Create a user -- the person of a user cannot be archived using this
    # search result handler.
    UserFactory(address_book, u'Ben', u'Utzer', u'ben@example.com',
                u'12345678', [], keywords=[u'church'])
    browser.login('mgr')
    browser.keyword_search('church')
    # Only the selected persons get archived. Deselected persons will not:
    browser.getControl(name='persons:list').getControl(
        value="Person-2").selected = False  # This this the person named "Koch"
    browser.getControl('Apply on selected persons').displayValue = [
        'Archive']
    browser.getControl(name='form.buttons.apply').click()
    # The number of persons for archival is shown on the question screen:
    # (There are 3 persons with the church keyword in the fixture, one got
    # deselected but there is additionally a newly created user.)
    assert ['3'] == browser.etree.xpath(
        '//span[@id="form-widgets-count"]/text()')
    assert ('You are not able to archive a person who is referenced.'
            in browser.contents)

    assert browser.SEARCH_ARCHIVE_URL == browser.url
    browser.getControl('Yes, archive').click()
    assert 'Selected persons archived: 2' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    # Only the two non-users got archived:
    assert 'Koch' in browser.contents
    assert 'Utzer' in browser.contents
    assert 'Liebig' not in browser.contents
    assert 'Velleuer' not in browser.contents


def test_archive__ArchiveForm__2(search_data, browser):
    """It can be cancelled."""
    browser.login('mgr')
    browser.keyword_search('church', 'Archive')
    # Selecting the `cancel` button leads to the person list without archiving
    # anybody:
    browser.getControl('No, cancel').click()
    assert 'Archiving canceled.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    assert 'Koch' in browser.contents
    assert 'Liebig' in browser.contents
    assert 'Velleuer' in browser.contents


@pytest.mark.parametrize('role', ['editor', 'visitor'])
def test_archive__ArchiveForm__3(search_data, browser, role):
    """It cannot be accessed by non-admin users."""
    browser.login(role)
    browser.keyword_search('church')
    # There is no archive option which can be applied:
    assert (search_result_handlers_without_archive_for_editor
            == browser.getControl('Apply on selected persons').displayOptions)
    browser.assert_forbidden(browser.SEARCH_ARCHIVE_URL)


@pytest.mark.parametrize('role', ['archivist', 'archive-visitor'])
def test_archive__ArchiveForm__4(address_book, browser, role):
    """It cannot be accessed by the archive roles."""
    browser.login(role)
    browser.assert_forbidden(browser.SEARCH_ARCHIVE_URL)


def test_archive__ArchiveForm__5(search_data, browser_request, browser):
    """It is only shown in the options list if archive is enabled."""
    address_book = search_data
    address_book.deselected_tabs = {'Archive'}

    browser.login('mgr')
    browser.keyword_search('church')
    # There is no archive option which can be applied:
    assert (search_result_handlers_without_archive_for_mgr
            == browser.getControl('Apply on selected persons').displayOptions)

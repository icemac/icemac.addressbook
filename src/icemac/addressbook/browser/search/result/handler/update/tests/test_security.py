import pytest
from icemac.addressbook.testing import Browser, assert_forbidden


@pytest.mark.parametrize('username', ('visitor', 'editor'))
def test_update__security__1(search_data, browser, username):
    """Some roles are not able to see the update search result handler."""
    browser.login(username)
    browser.keyword_search('church')
    assert ['XLS export main (Exports person data and main addresses resp. '
            'phone numbers.)',
            'XLS export complete (Exports person data and all addresses '
            'resp. phone numbers.)',
            'E-Mail (Creates a link to send e-mails.)',
            'Names (Comma separated list of person names.)',
            'Checklist (List of person names with check-boxes.)',
            "iCalendar export birthday (Export person's birthdays as .ics "
            "file.)"] == browser.getControl(
                'Apply on selected persons').displayOptions


@pytest.mark.parametrize(
    'url', (Browser.SEARCH_MULTI_UPDATE_URL,
            Browser.SEARCH_MULTI_UPDATE_CHOOSE_FIELD_URL,
            Browser.SEARCH_MULTI_UPDATE_ENTER_VALUE_URL,
            Browser.SEARCH_MULTI_UPDATE_CHECK_RESULT_URL,
            Browser.SEARCH_MULTI_UPDATE_COMPLETE_URL))
@pytest.mark.parametrize('username', ('visitor', 'editor'))
def test_update__security__2(search_data, browser, url, username):
    """Some roles are not able to access update search result handler URLs.

    This is even right when he knows the URLs.

    """
    assert_forbidden(browser, username, url)

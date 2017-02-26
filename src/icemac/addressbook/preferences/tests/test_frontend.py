import pytest


@pytest.mark.webdriver
def test_preferences__1(address_book, webdriver):
    """Testing JS funtions of preferences frontend."""
    prefs = webdriver.prefs
    webdriver.login('mgr', prefs.PREFS_URL)
    # Preference groups are closed by default, fields are not visible:
    prefs.wait_for_fields_visible(False)
    prefs.toggle_group('personLists')
    prefs.wait_for_fields_visible(True)
    # Clicking on a form element does not close the group:
    prefs.select_column('person -- birth date')
    prefs.wait_for_fields_visible(True)
    prefs.toggle_group('personLists')
    prefs.wait_for_fields_visible(False)

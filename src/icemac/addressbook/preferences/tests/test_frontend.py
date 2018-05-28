import pytest


@pytest.mark.webdriver
def test_preferences__1_webdriver(address_book, webdriver, FullPersonFactory):
    """Testing JS functions of preferences front-end."""
    FullPersonFactory(address_book, u'Tester')
    prefs = webdriver.prefs
    webdriver.login('mgr', prefs.PREFS_URL)

    # Preference groups are closed by default, fields are not visible:
    prefs.wait_for_fields_visible(False)
    prefs.toggle_group('personLists')
    prefs.wait_for_fields_visible(True)
    # Elements can be removed from the columns list:
    prefs.remove_first_column_selected_for_person_list()

    # New elements can be added:
    prefs.select_column_for_person_list("postal address -- city")
    prefs.select_column_for_person_list("person -- notes")

    # the group can be closed again:
    prefs.toggle_group('personLists')
    prefs.wait_for_fields_visible(False)

    prefs.submit()
    assert 'Data successfully updated.' == webdriver.message

    personlist = webdriver.personlist
    assert ['first name', 'city', 'notes'] == personlist.column_headlines

    # The selected columns are stored and rendered correctly when visiting
    # the form again:
    webdriver.open(prefs.PREFS_URL)
    prefs.wait_for_fields_visible(False)
    prefs.toggle_group('personLists')
    prefs.wait_for_fields_visible(True)
    assert [
        u'person -- first name',
        u'postal address -- city',
        u'person -- notes',
    ] == prefs.selected_columns_for_person_list

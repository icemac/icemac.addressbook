import pytest


@pytest.mark.webdriver
def test_preferences__1(address_book, webdriver):
    """Testing JS funtions of preferences frontend."""
    sel = webdriver.login('mgr')
    sel.open("/ab/++preferences++/ab")
    # Preference groups are closed by default, fields are not visible:
    sel.assertNotVisible("css=#form-widgets-columns-row")
    # After opening the group the field is shown:
    sel.click("//fieldset[@class='personLists']/legend")
    sel.waitForVisible("css=#form-widgets-columns-row")
    # Clicking on a form element does not close the group:
    sel.addSelection("id=form-widgets-columns-from",
                     "label=person -- birth date")
    sel.click("name=from2toButton")
    sel.assertVisible("css=#form-widgets-columns-row")
    # Clicking on the legend closes the group:
    sel.click("//fieldset[@class='personLists']/legend")
    sel.waitForNotVisible("css=#form-widgets-columns-row")

import icemac.addressbook.testing


class FrontEndTests(icemac.addressbook.testing.SeleniumTestCase):
    """Testing JS funtions of preferences frontend."""

    def test_preferences_front_end(self):
        self.login('mgr')
        sel = self.selenium
        sel.open("/ab/++preferences++/ab")
        # Preference groups are closed by default, fields are not visible:
        sel.assertNotVisible("css=#form-widgets-columns-row")
        # After opening the group the field is shown:
        sel.click("css=legend")
        sel.waitForVisible("css=#form-widgets-columns-row")
        # Clicking on a form element does not close the group:
        sel.addSelection("id=form-widgets-columns-from",
                         "label=person -- birth date")
        sel.click("name=from2toButton")
        sel.assertVisible("css=#form-widgets-columns-row")
        # Clicking on the legend closes the group:
        sel.click("css=legend")
        sel.waitForNotVisible("css=#form-widgets-columns-row")

import icemac.addressbook.testing
import icemac.addressbook.browser.testing


class PersonTableSTests(icemac.addressbook.testing.SeleniumTestCase):
    """Selenium testing ..personlist.PersonTable."""

    layer = icemac.addressbook.browser.testing.SELENIUM_SEARCH_LAYER

    def test_checkall_checkbox_deselects_and_reselects_all_persons(self):
        self.login('visitor', 'visitor')
        s = self.selenium
        s.open('/ab/@@multi_keyword.html')
        s.addSelection('id=form-widgets-keywords', 'label=family')
        s.clickAndWait('id=form-buttons-search')
        s.assertValue('name=persons:list', 'on')
        # Deselect
        s.click('css=input.checkall')
        s.assertValue('name=persons:list', 'off')
        # Reselect
        s.click('css=input.checkall')
        s.assertValue('name=persons:list', 'on')

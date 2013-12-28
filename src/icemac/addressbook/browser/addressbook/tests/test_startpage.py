from mock import patch
import icemac.addressbook.testing


class DispatchFTests(icemac.addressbook.testing.BrowserTestCase):
    """Functional testing ..startpage.Dispatch."""

    def test_startpage_by_defaut_redirects_to_welcome_page(self):
        browser = self.get_browser('visitor')
        browser.open('http://localhost/ab')
        self.assertEqual('http://localhost/ab/@@welcome.html', browser.url)


class DispatchSTests(icemac.addressbook.testing.SeleniumTestCase):
    """Selenium testing ..startpage.Dispatch."""

    def test_startpage_redirects_to_page_set_on_address_book(self):
        self.login()
        sel = self.selenium
        sel.open('/ab/@@edit.html')
        sel.select('id=form-widgets-startpage', 'label=Search')
        sel.type('id=form-widgets-title', 'Test')
        sel.clickAndWait('id=form-buttons-apply')
        sel.open('/ab')
        sel.assertLocation('http://%s/ab/@@search.html' % sel.server)

    def test_startpage_redirects_to_welcome_page_if_access_not_allowed(self):
        self.login()
        sel = self.selenium
        sel.open('/ab/@@edit.html')
        sel.select('id=form-widgets-startpage', 'label=Search')
        sel.type('id=form-widgets-title', 'Test')
        sel.clickAndWait('id=form-buttons-apply')
        can_access_uri_part = (
            'icemac.addressbook.browser.addressbook.startpage.'
            'can_access_uri_part')
        with patch(can_access_uri_part, return_value=False):
            sel.open('/ab')
            sel.assertLocation('http://%s/ab/@@welcome.html' % sel.server)

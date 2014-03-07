import icemac.addressbook.browser.testing
import icemac.addressbook.testing


class ExportTests(icemac.addressbook.testing.BrowserTestCase):
    """Testing ..export.ExportList.

    Actual exporters are tested in their modules.

    """
    layer = icemac.addressbook.browser.testing.WSGI_SEARCH_LAYER

    def test_renders_advice_if_there_are_no_exporters(self):
        browser = self.get_browser('visitor')
        browser.open('http://localhost/ab/@@person-list.html')
        browser.getLink('Hohmuth').click()
        browser.getControl('Export').click()
        self.assertIn('You did not enter enough data of the person, '
                      'so no export is possible.', browser.contents)

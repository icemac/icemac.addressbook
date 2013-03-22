import icemac.addressbook.testing


class PrefGroupEditForm(icemac.addressbook.testing.BrowserTestCase):
    """Testing ..browser.PrefGroupEditForm."""

    def test_redirects_to_self_after_cancel(self):
        browser = self.get_browser('visitor')
        url = 'http://localhost/ab/++preferences++/ab.timeZone/@@index.html'
        browser.open(url)
        self.assertEqual(
            ['UTC'], browser.getControl('Time zone').displayValue)
        browser.getControl('Time zone').displayValue = ['Navajo']
        browser.getControl('Cancel').click()
        # After redirect the original value is restored in the field:
        self.assertEqual(
            ['UTC'], browser.getControl('Time zone').displayValue)
        self.assertEqual(url, browser.url)

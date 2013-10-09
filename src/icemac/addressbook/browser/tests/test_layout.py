import icemac.addressbook.testing


class LayoutTests(icemac.addressbook.testing.BrowserTestCase):
    """Testing ../layout.pt."""

    def test_renders_addressbook_title_in_title_tag_and_h1(self):
        self.layer['addressbook'].title = u'My addresses'
        browser = self.get_browser()
        browser.open('http://localhost/ab')
        self.assertEqual('My addresses', browser.title)
        self.assertEqual(
            'My addresses', browser.etree.xpath('//h1/span')[0].text)

    def test_falls_back_to_default_title_if_no_title_set(self):
        browser = self.get_browser()
        browser.open('http://localhost/ab')
        self.assertEqual('icemac.addressbook', browser.title)
        self.assertEqual(
            'icemac.addressbook', browser.etree.xpath('//h1/span')[0].text)

    def test_renders_default_title_on_root_page(self):
        browser = self.get_browser('mgr')  # need to log in to avoid HTTP-401
        browser.open('http://localhost')
        self.assertEqual('icemac.addressbook', browser.title)
        self.assertEqual(
            'icemac.addressbook', browser.etree.xpath('//h1/span')[0].text)

    def test_renders_default_favicon_on_root_page(self):
        browser = self.get_browser('mgr')  # need to log in to avoid HTTP-401
        browser.open('http://localhost')
        self.assertIn('href="/++resource++img/favicon-red.png"',
                      browser.contents)

    def test_renders_selected_favicon_inside_address_book(self):
        self.layer['addressbook'].favicon = (
            u'/++resource++img/favicon-green.png')
        browser = self.get_browser()
        browser.open('http://localhost/ab')
        self.assertIn('href="/++resource++img/favicon-green.png"',
                      browser.contents)

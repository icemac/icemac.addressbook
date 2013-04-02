import icemac.addressbook.testing


class PersonListTests(icemac.addressbook.testing.BrowserTestCase):
    """Testing ..list.PersonList."""

    def test_list_is_initially_empty(self):
        browser = self.get_browser('visitor')
        browser.open('http://localhost/ab')
        browser.getLink('Person list').click()
        self.assertEqual('http://localhost/ab/@@person-list.html', browser.url)
        self.assertIn(
            'There are no persons entered yet, click on "Add person" to '
            'create one.', browser.contents)


class SecurityTests(icemac.addressbook.testing.BrowserTestCase):
    """Security testing ..list.PersonList."""

    def test_visitor_is_not_allowed_to_add_new_persons(self):
        from mechanize import LinkNotFoundError
        browser = self.get_browser('visitor')
        browser.open('http://localhost/ab/@@person-list.html')
        with self.assertRaises(LinkNotFoundError):
            browser.getLink('person')

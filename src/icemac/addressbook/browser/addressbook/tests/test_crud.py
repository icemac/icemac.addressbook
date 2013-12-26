import icemac.addressbook.testing


class CRUDTests(icemac.addressbook.testing.BrowserTestCase):
    """Testing ..crud.*.

    Without add as it needs JavaScript. See AddressbookEditSeleniumTests.

    """
    def test_edit_can_be_canceled(self):
        self.layer['addressbook'].title = u'ftest-ab'
        browser = self.get_browser('mgr')
        browser.open('http://localhost/ab/@@edit.html')
        self.assertEqual('ftest-ab', browser.getControl('title').value)
        browser.getControl('title').value = 'fancy book'
        browser.getControl('Cancel').click()
        self.assertEqual(
            ['No changes were applied.'], browser.get_messages())
        self.assertEqual('ftest-ab', browser.getControl('title').value)

    def test_editor_is_not_allowed_to_delete_all_persons_in_address_book(self):
        from mechanize import HTTPError
        browser = self.get_browser('editor')
        with self.assertRaises(HTTPError) as err:
            browser.open('http://localhost/ab/@@delete_content.html')
        self.assertEqual('HTTP Error 403: Forbidden', str(err.exception))

    def test_visitor_is_not_allowed_to_delete_all_persons_in_address_book(
            self):
        from mechanize import HTTPError
        browser = self.get_browser('visitor')
        with self.assertRaises(HTTPError) as err:
            browser.open('http://localhost/ab/@@delete_content.html')
        self.assertEqual('HTTP Error 403: Forbidden', str(err.exception))

    def test_administrator_is_able_to_delete_all_persons_in_address_book(self):
        # The Administrator is able to delete all persons in the address
        # book on the edit form. Users are not deleted because the are
        # referenced as a safty belt so the current user does not delete his
        # credencials.

        # Make sure there are some persons (with addresses) and some users
        # in the address book:
        from icemac.addressbook.testing import (
            create_person, create_user, create_postal_address)
        ab = self.layer['addressbook']
        create_person(ab, ab, last_name=u'Tester')
        create_person(ab, ab, last_name=u'Tester 2')
        create_user(
            ab, ab, u'Hans', u'User', u'hans@user.de', u'asdf', ['Visitor'])
        create_user(
            ab, ab, u'Kurt', u'Utzr', u'kurt@utzr.ch', u'asdf', ['Editor'])
        t3 = create_person(ab, ab, last_name=u'Tester 3')
        create_postal_address(ab, t3, city=u'Hettstedt')

        # To delete all persons in the address book, the Adminstrator has to
        # open the `edit address book` form and select the `Delete all
        # persons in address book` button there. An `are you sure` form is
        # displayed:
        browser = self.get_browser('mgr')
        browser.open('http://localhost/ab/@@edit.html')
        browser.getControl('Delete all persons in address book').click()
        self.assertEqual(
            'http://localhost/ab/@@delete_content.html', browser.url)

        # When the adminstrator decides not to delete the persons he is led
        # back to the address book's edit form:
        self.assertIn(
            'Do you really want to delete all persons in this address book?',
            browser.contents)
        # The number of persons in the address book is displayed:
        self.assertIn(
            'class="text-widget int-field">5</span>', browser.contents)
        browser.getControl('No, cancel').click()
        self.assertEqual(['Deletion canceled.'], browser.get_messages())
        self.assertEqual('http://localhost/ab/@@edit.html', browser.url)

        # When he decides to delete all persons he is led back to the person
        # list where only the users are still shown:
        browser.getControl('Delete all persons in address book').click()
        browser.getControl('Yes').click()
        self.assertEqual(
            ['Address book contents deleted.'], browser.get_messages())
        self.assertEqual('http://localhost/ab/person-list.html', browser.url)
        self.assertIn('Person-3">User', browser.contents)
        self.assertIn('Person-4">Utzr', browser.contents)


class AddressbookEditSeleniumTests(
        icemac.addressbook.testing.SeleniumTestCase):
    """Selenium testing .crud.EditForm."""

    def test_new_address_book_can_be_added_and_edited(self):
        # Only managers are allowed to create address books:
        self.login()
        sel = self.selenium
        # On the start page there is a link to add an address book:
        sel.clickAndWait('link=address book')
        sel.type('id=form-widgets-title', 'test book')

        # Default value of favicon is pre-selected:
        sel.assertCssCount(
            'css=.ui-selected '
            'img[src="/++resource++img/favicon-red-preview.png"]', 1)
        sel.clickAt('form-widgets-favicon-1', '20,20')
        sel.clickAndWait('form-buttons-add')
        self.assertMessage('"test book" added.')
        sel.assertLocation('http://%s/AddressBook/@@welcome.html' % sel.server)
        # Editing is done in master data section:
        sel.clickAndWait('link=Master data')
        sel.clickAndWait('link=Address book')
        self.assertEqual('http://%s/AddressBook/@@edit.html' % sel.server,
                         sel.getLocation())
        # The add form actually stored the values:
        sel.assertValue('id=form-widgets-title', 'test book')
        sel.assertCssCount('css=#form-widgets-favicon-1.ui-selected', 1)
        # The edit form is able to change the data:
        sel.type('id=form-widgets-title', 'ftest book')
        sel.clickAt('form-widgets-favicon-0', '20,20')
        sel.clickAndWait('form-buttons-apply')
        self.assertMessage('Data successfully updated.')
        # The edit form submits to itself and shows the stored data:
        sel.assertValue('id=form-widgets-title', 'ftest book')
        sel.assertCssCount('css=#form-widgets-favicon-0.ui-selected', 1)


class SecurityTests(icemac.addressbook.testing.BrowserTestCase):
    """Security testing ..crud.*."""

    def test_editor_is_not_allowed_to_edit_address_books_data(self):
        from mechanize import LinkNotFoundError, HTTPError
        # There is no link to edit the address book's data (title) because
        # the editor is not allowed to do so:
        browser = self.get_browser('editor')
        browser.open('http://localhost/ab/@@masterdata.html')
        with self.assertRaises(LinkNotFoundError):
            browser.getLink('Address book')
        # Even opening the URL is not possible:
        with self.assertRaises(HTTPError) as err:
            browser.open('http://localhost/ab/@@edit.html')
        self.assertEqual('HTTP Error 403: Forbidden', str(err.exception))

    def test_visitor_is_not_allowed_to_edit_address_books_data(self):
        from mechanize import LinkNotFoundError, HTTPError
        # There is no link to edit the address book's data (title) because
        # the visitor is not allowed to do so:
        browser = self.get_browser('visitor')
        browser.open('http://localhost/ab/@@masterdata.html')
        with self.assertRaises(LinkNotFoundError):
            browser.getLink('Address book')
        # Even opening the URL is not possible:
        with self.assertRaises(HTTPError) as err:
            browser.open('http://localhost/ab/@@edit.html')
        self.assertEqual('HTTP Error 403: Forbidden', str(err.exception))


class WelcomeTests(icemac.addressbook.testing.BrowserTestCase):
    """Testing ../welcome.pt."""

    def test_the_greeting_after_login_contains_the_address_book_title(self):
        self.layer['addressbook'].title = u'ftest-ab'
        browser = self.get_browser('visitor')
        browser.open('http://localhost/ab')
        self.assertIn(
            '<p>Welcome to ftest-ab. Please select one of the tabs above.</p>',
            browser.contents)

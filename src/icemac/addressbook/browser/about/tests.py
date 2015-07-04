import icemac.addressbook.testing


class AboutTests(icemac.addressbook.testing.BrowserTestCase):
    """Testing ..about."""

    # The about screen displays some information about the application, its
    # version and licenses. It is accessable everywhere in the application.

    def test_about_dialog_is_displayed_on_root_view(self):
        from icemac.addressbook import copyright
        from pkg_resources import get_distribution
        # The root view is basic auth protected, so we have to log-in to see
        # the root view.
        browser = self.get_browser('mgr')
        browser.open('http://localhost')
        # There is a link on the root view pointing to the about dialog:
        browser.getLink(id="about-view").click()
        self.assertEqual('http://localhost/@@about.html', browser.url)
        # The about dialog displays the version number of the address book:
        self.assertIn(get_distribution('icemac.addressbook').version,
                      browser.contents)
        # ... and the copyright string (it is contained twice, as the footer
        # contains it, too):
        self.assertEqual(2, browser.contents.count(copyright))
        # There is a link to VistaIco as the license for using the icons
        # requires this:
        self.assertEqual('http://www.vistaico.com',
                         browser.getLink('VistaICO.com').url)

    def test_about_dialog_is_displayed_on_login_screen(self):
        # The login screen can be accessed by anonymous users:
        browser = self.get_browser()
        browser.open('http://localhost/ab')
        # There is a link on the login view pointing to the about dialog:
        browser.getLink(id="about-view").click()
        self.assertEqual('http://localhost/@@about.html', browser.url)

    def test_about_dialog_is_displayed_inside_the_application(self):
        # The about screen can be accessed on every object, for example we
        # use a person:
        self.create_person(u'Tester')
        browser = self.get_browser('visitor')
        browser.open('http://localhost/ab/Person')
        browser.getLink(id="about-view").click()
        self.assertEqual('http://localhost/@@about.html', browser.url)

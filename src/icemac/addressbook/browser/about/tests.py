# The about screen displays some information about the application, its
# version and licenses. It is accessable everywhere in the application.

ABOUT_URL = 'http://localhost/@@about.html'


def test_about__About__1(address_book, browser):
    """The about dialog is displayed on the root view."""
    from icemac.addressbook import copyright
    from pkg_resources import get_distribution
    # The root view is basic auth protected, so we have to log-in to see
    # the root view.
    browser.login('mgr')
    browser.open('http://localhost')
    # There is a link on the root view pointing to the about dialog:
    browser.getLink(id="about-view").click()
    assert ABOUT_URL == browser.url
    # The about dialog displays the version number of the address book:
    assert get_distribution('icemac.addressbook').version in browser.contents
    # ... and the copyright string (it is contained twice, as the footer
    # contains it, too):
    assert 2 == browser.contents.count(copyright)
    # There is a link to VistaIco as the license for using the icons
    # requires this:
    assert 'http://www.vistaico.com' == browser.getLink('VistaICO.com').url


def test_about__About__2(address_book, browser):
    """The about dialog is displayed on login screen."""
    # The login screen can be accessed by anonymous users:
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    # There is a link on the login view pointing to the about dialog:
    browser.getLink(id="about-view").click()
    assert ABOUT_URL == browser.url


def test_about__About__3(address_book, PersonFactory, browser):
    """The about dialog is displayed inside the application."""
    # The about screen can be accessed on every object, for example we
    # use a person:
    PersonFactory(address_book, u'Tester')
    browser.login('visitor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getLink(id="about-view").click()
    assert ABOUT_URL == browser.url

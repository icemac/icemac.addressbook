# The about screen displays some information about the application, its
# version and licenses. It is accessible nearly everywhere in the application.
from icemac.addressbook import copyright
from pkg_resources import get_distribution
import mock
import os

ABOUT_URL = 'http://localhost/ab/@@about.html'


def test_about__About__2(address_book, browser):
    """The about dialog is displayed on login screen."""
    # The login screen can be accessed by anonymous users:
    browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
    # There is a link on the login view pointing to the about dialog:
    browser.getLink("About").click()
    assert ABOUT_URL == browser.url
    # The about dialog displays the version number of the address book:
    assert get_distribution('icemac.addressbook').version in browser.contents
    # ... and the copyright string (it is contained twice, as the footer
    # contains it, too):
    assert 2 == browser.contents.count(copyright)
    # There is a link to VistaIco as the license for using the icons
    # requires this:
    assert 'http://www.vistaico.com' == browser.getLink('VistaICO.com').url


def test_about__About__3(address_book, PersonFactory, browser):
    """The about dialog is displayed inside the application."""
    # The about screen can be accessed on every object, for example we
    # use a person:
    PersonFactory(address_book, u'Tester')
    browser.login('visitor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getLink("About").click()
    assert ABOUT_URL == browser.url


def test_footer__ImprintLink__title__1(address_book, browser):
    """It renders an imprint link if the necessary env vars are set."""
    data = {'AB_LINK_IMPRINT_TEXT': 'My Imprint',
            'AB_LINK_IMPRINT_URL': 'https://imprint.example.com'}
    with mock.patch.dict(os.environ, data):
        browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
        tags = browser.etree.xpath('//*[@id="foot"]/ul/li/a')
        assert len(tags) == 1
        tag = tags[0]
        assert tag.get('target') == '_blank'
        assert tag.get('href') == 'https://imprint.example.com'
        assert tag.iterchildren().next().text == 'My Imprint'


def test_footer__DataprotectionLink__title__1(address_book, browser):
    """It renders a data protection link if the necessary env vars are set."""
    data = {'AB_LINK_DATAPROTECTION_TEXT': 'Datenschutz',
            'AB_LINK_DATAPROTECTION_URL': 'https://daten.example.com'}
    with mock.patch.dict(os.environ, data):
        browser.open(browser.ADDRESS_BOOK_DEFAULT_URL)
        tags = browser.etree.xpath('//*[@id="foot"]/ul/li/a')
        assert len(tags) == 1
        tag = tags[0]
        assert tag.get('target') == '_blank'
        assert tag.get('href') == 'https://daten.example.com'
        assert tag.iterchildren().next().text == 'Datenschutz'

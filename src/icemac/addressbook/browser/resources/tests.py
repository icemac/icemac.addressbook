from icemac.addressbook.testing import WebdriverPageObjectBase, Webdriver
import pytest


def test_resources__1(address_book, browser):
    """Image resources can be delivered to the browser."""
    browser.open('http://localhost/++resource++img/Symbol-Information.png')
    assert '200 Ok' == browser.headers['status']


class POPerson(WebdriverPageObjectBase):
    """Webdriver page object for the person page."""

    paths = [
        'PERSON_EDIT_URL',
    ]

    def get_hints(self):
        return self._selenium.getText("css=div.hint")


Webdriver.attach(POPerson, 'person')


@pytest.mark.webdriver
def test_resources__form_js__render_field_hint__1(
        address_book, FullPersonFactory, webdriver):
    """It renders the titles of the fields as separate hint."""
    FullPersonFactory(address_book, u'Tester')
    person_page = webdriver.person
    webdriver.login('editor', person_page.PERSON_EDIT_URL)
    assert "e. g. company name or c/o" == person_page.get_hints()

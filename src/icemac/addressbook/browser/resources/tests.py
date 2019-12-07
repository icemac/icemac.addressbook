# -*- coding: utf-8 -*-
from icemac.addressbook.testing import WebdriverPageObjectBase, Webdriver
import pytest


def test_resources__1(address_book, browser):
    """Image resources can be delivered to the browser."""
    browser.open('http://localhost/++resource++img/Symbol-Error.png')
    assert '200 Ok' == browser.headers['status']


class POPerson(WebdriverPageObjectBase):
    """Webdriver page object for the person page."""

    paths = [
        'PERSON_EDIT_URL',
    ]

    def get_hints(self):
        return self._selenium.find_element_by_css_selector("div.hint").text

    @property
    def keywords(self):
        elements = self._selenium.find_elements_by_xpath(
            '//li[@class="select2-selection__choice"]')
        return [x.get_attribute('title') for x in elements]

    @keywords.setter
    def keywords(self, values):
        self.select_from_drop_down(values)

    def submit(self):
        self._selenium.find_element_by_id("form-buttons-apply").click()


Webdriver.attach(POPerson, 'person')


@pytest.mark.webdriver
def test_resources__form_js__render_field_hint__1_webdriver(address_book, FullPersonFactory, webdriver):  # noqa
    """It renders the titles of the fields as separate hint."""
    FullPersonFactory(address_book, u'Tester')
    person_page = webdriver.person
    webdriver.login('editor', person_page.PERSON_EDIT_URL)
    assert "e. g. company name or c/o" == person_page.get_hints()


@pytest.mark.webdriver
def test_resources__form_js__select2__1_webdriver(address_book, FullPersonFactory, KeywordFactory, webdriver):  # noqa
    """It renders the keywords widget using select2."""
    FullPersonFactory(address_book, u'Tester')
    KeywordFactory(address_book, u'foo')
    KeywordFactory(address_book, u'baz')
    KeywordFactory(address_book, u'bar')
    person_page = webdriver.person
    webdriver.login('editor', person_page.PERSON_EDIT_URL)
    person_page.keywords = [u'foo', u'bar']
    person_page.submit()
    assert 'Data successfully updated.' == webdriver.message

    # Test whether the values where stored:
    webdriver.login('editor', person_page.PERSON_EDIT_URL)
    assert [u'bar', u'foo'] == person_page.keywords

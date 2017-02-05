import pytest


def test_resources__1(address_book, browser):
    """Image resources can be delivered to the browser."""
    browser.open('http://localhost/++resource++img/Symbol-Information.png')
    assert '200 Ok' == browser.headers['status']


@pytest.mark.webdriver
def test_resources__form_js__render_field_hint__1(
        address_book, FullPersonFactory, webdriver):
    """It renders the titles of the fields as separate hint."""
    FullPersonFactory(address_book, u'Tester')
    sel = webdriver.login('editor')
    sel.open('/ab/Person')
    sel.verifyText(
        "css=#IcemacAddressbookAddressPostaladdress_0-widgets-"
        "IcemacAddressbookAddressPostaladdress_0-address_prefix-row div.hint",
        "e. g. company name or c/o")

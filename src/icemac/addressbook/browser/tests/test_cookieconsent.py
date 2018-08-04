from ..cookieconsent import CookieConsentViewlet
from icemac.addressbook.browser.interfaces import IFanstaticViewletManager
from icemac.addressbook.testing import Webdriver
from icemac.addressbook.testing import WebdriverPageObjectBase
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
import mock
import os
import pytest
import zope.component


@zope.interface.implementer(IFanstaticViewletManager)
class FakeFanstaticViewletManager(object):
    """Fake FanstaticViewletManager."""


@zope.interface.implementer(zope.browser.interfaces.IBrowserView)
class FakeBrowserView(object):
    """Fake BrowserView."""


def test_cookieconsent__CookieConsentViewlet__update__1(
        address_book, RequestFactory):
    """It contains the data protection URL and link text if the URL is set."""
    viewlet = zope.component.getMultiAdapter(
        (address_book,
         RequestFactory(),
         FakeBrowserView(),
         FakeFanstaticViewletManager()),
        zope.viewlet.interfaces.IViewlet,
        name='CookieConsent')
    assert isinstance(viewlet, CookieConsentViewlet)
    data = {'AB_LINK_DATAPROTECTION_URL': 'https://datapro.example.com'}
    with mock.patch.dict(os.environ, data):
        viewlet.update()
        result = viewlet.render()
    assert '"href": "https://datapro.example.com"' in result
    assert '"link": "Read more."' in result


def test_cookieconsent__CookieConsentViewlet__update__2(
        address_book, RequestFactory):
    """It contains a null data protection URL and null link text if ...

    ... URL isn't set.
    """
    viewlet = zope.component.getMultiAdapter(
        (address_book,
         RequestFactory(),
         FakeBrowserView(),
         FakeFanstaticViewletManager()),
        zope.viewlet.interfaces.IViewlet,
        name='CookieConsent')
    data = {'AB_LINK_DATAPROTECTION_URL': ''}
    with mock.patch.dict(os.environ, data):
        viewlet.update()
        result = viewlet.render()
    assert '"href": null' in result
    assert '"link": null' in result


@pytest.fixture('function')
def po_cookieconsent_webdriver():
    """Webdriver page object for the cookie consent dialog."""
    class POCookieConsent(WebdriverPageObjectBase):
        paths = [
            'ADDRESS_BOOK_DEFAULT_URL',
        ]

        class Button(object):

            def __init__(self, driver, selector, expect_to_be_visible):
                self.driver = driver
                self.selector = selector
                self.wait = WebDriverWait(driver, 3)  # seconds
                self.el = driver.find_element_by_css_selector(selector)
                if expect_to_be_visible:
                    self.wait.until(expected_conditions.visibility_of(self.el))

            @property
            def is_displayed(self):
                return self.el.is_displayed()

            def click(self):
                self.el.click()
                self.wait.until(
                    expected_conditions.invisibility_of_element_located(
                        (By.CSS_SELECTOR, self.selector)))

        def _get_button(self, expect_to_be_visible):
            return self.Button(
                self._selenium,
                '.cc-compliance .cc-dismiss',
                expect_to_be_visible)

        @property
        def button_is_displayed(self):
            button = self._get_button(expect_to_be_visible=True)
            return button.is_displayed

        @property
        def button_is_not_displayed(self):
            button = self._get_button(expect_to_be_visible=False)
            return not button.is_displayed

        def button_click(self):
            button = self._get_button(expect_to_be_visible=True)
            button.click()

    Webdriver.attach(POCookieConsent, 'cookieconsent')
    yield
    Webdriver.detach(POCookieConsent, 'cookieconsent')


@pytest.mark.webdriver
def test_cookieconsent__CookieConsentViewlet__render__1_webdriver(address_book, po_cookieconsent_webdriver, webdriver):  # noqa E501
    """It allows to dismiss the cookie consent dialog."""
    cookieconsent = webdriver.cookieconsent
    webdriver.login('visitor', cookieconsent.ADDRESS_BOOK_DEFAULT_URL)
    assert cookieconsent.button_is_displayed
    # Clicking the button dismisses the dialog:
    cookieconsent.button_click()
    assert cookieconsent.button_is_not_displayed
    # It does not show up again on other pages:
    webdriver.open(cookieconsent.ADDRESS_BOOK_DEFAULT_URL)
    assert cookieconsent.button_is_not_displayed

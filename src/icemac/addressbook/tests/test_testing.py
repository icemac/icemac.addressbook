import icemac.addressbook.testing
import icemac.addressbook.tests


ZCML_LAYER = icemac.addressbook.testing.SecondaryZCMLLayer(
    'GetMessagesZCML', __name__, icemac.addressbook.tests,
    [icemac.addressbook.testing.ZCML_LAYER], filename='testing.zcml')
ZODB_LAYER = icemac.addressbook.testing.ZODBLayer(
    'GetMessagesZODB', ZCML_LAYER)
TEST_BROWSER_LAYER = icemac.addressbook.testing.TestBrowserLayer(
    'GetMessagesTestBrowser', ZODB_LAYER)


class GetMessagesTests(icemac.addressbook.testing.BrowserTestCase):
    """Testing ..testing.get_messages()."""

    layer = TEST_BROWSER_LAYER

    def callFUT(self, browser):
        from icemac.addressbook.testing import get_messages
        return get_messages(browser)

    def test_requires_an_z3c_etestbrowser(self):
        from zope.app.wsgi.testlayer import Browser
        browser = Browser(wsgi_app=self.layer['wsgi_app'])
        with self.assertRaises(ValueError) as err:
            self.callFUT(browser)
        self.assertEqual(
            'browser must be z3c.etestbrowser.wsgi.ExtendedTestBrowser',
            str(err.exception))

    def test_no_message_results_in_an_empty_list(self):
        browser = self.get_browser('mgr')
        browser.open('http://localhost')
        self.assertEqual([], self.callFUT(browser))

    def test_messages_are_returned_as_list(self):
        browser = self.get_browser('mgr')
        browser.open('http://localhost/@@test-get-messages.tst?msg=foo')
        browser.open('http://localhost/@@test-get-messages.tst?msg=blah')
        self.assertEqual("Message u'blah' sent.", browser.contents)
        browser.open('http://localhost')
        self.assertEqual(['foo', 'blah'], self.callFUT(browser))

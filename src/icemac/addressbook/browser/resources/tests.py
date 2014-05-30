import icemac.addressbook.testing
import unittest


class ResourcesTests(unittest.TestCase,
                     icemac.addressbook.testing.BrowserMixIn):
    """Testing resources."""

    layer = icemac.addressbook.testing.TEST_BROWSER_LAYER

    def test_image_resources_can_be_delivered(self):
        browser = self.get_browser()
        browser.open(
            'http://localhost/++resource++img/Symbol-Information.png')
        self.assertEqual('200 Ok', browser.headers['status'])

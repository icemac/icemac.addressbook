import icemac.addressbook.testing
import unittest


class ResourcesTests(unittest.TestCase):
    """Testing resources."""

    layer = icemac.addressbook.testing.WSGI_TEST_BROWSER_LAYER

    def test_image_resources_can_be_delivered(self):
        browser = icemac.addressbook.testing.Browser()
        browser.open('http://localhost/++resource++img/favicon.ico')
        self.assertEqual('200 Ok', browser.headers['status'])

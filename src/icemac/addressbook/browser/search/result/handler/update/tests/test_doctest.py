import icemac.addressbook.browser.testing
import icemac.addressbook.testing


def test_suite():
    return icemac.addressbook.testing.DocFileSuite(
        "update.txt",
        package="icemac.addressbook.browser.search.result.handler.update",
        layer=icemac.addressbook.browser.testing.WSGI_SEARCH_LAYER)

from ..breadcrumb import IBreadcrumb, Breadcrumb
from zope.testbrowser.browser import HTTPError
import mock
import pytest
import zope.interface.verify


def test_breadcrumb__Breadcrumb__1(zcmlS):
    """It fulfills the interface definition."""
    breadcrumb = Breadcrumb(None, None)
    with mock.patch.object(breadcrumb, 'url'):
        with mock.patch('zope.traversing.api.getParent'):
            zope.interface.verify.verifyObject(IBreadcrumb, breadcrumb)


def test_breadcrumb__Breadcrumb____repr____1():
    """It renders a nice repr."""
    class MyBreadcrumb(Breadcrumb):
        title = u'my title'

    breadcrumb = MyBreadcrumb(None, None)
    assert ("<icemac.addressbook.browser.tests.test_breadcrumb.MyBreadcrumb:"
            " u'my title'>" == repr(breadcrumb))


def test_breadcrumb__NotFoundBreadcrumb__1(address_book, browser):
    """It renders a nice title in the breadcrumbs if a page cannot be found."""
    browser.login('visitor')
    with pytest.raises(HTTPError) as err:
        browser.open('http://localhost/I-do-not-exist')
    assert 'HTTP Error 404: Not Found' == str(err.value)
    assert '>Not Found<' in browser.contents

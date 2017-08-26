from ..breadcrumb import IBreadcrumb, Breadcrumb
import mock
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

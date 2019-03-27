import pytest


def test_inspector__Inspector__show_context__1(address_book, browser):
    """It renders context information on a view."""
    browser.login('globalmgr')
    browser.open(browser.INSPECTOR_VIEW_URL)
    assert "PersonList u'person-list.html'" in browser.contents
    # the base classes of the view
    assert (
        "(&lt;class 'icemac.addressbook.browser.person.list.PersonList'&gt;, "
        "&lt;class 'z3c.pagelet.browser.BrowserPagelet'&gt;)" in
        browser.contents)
    # an interface of the view
    assert 'z3c.pagelet.interfaces.IPagelet' in browser.contents


def test_inspector__Inspector__show_context__2(address_book, browser):
    """It renders context information on an object."""
    browser.login('globalmgr')
    browser.open(browser.INSPECTOR_OBJECT_URL)
    # Class of context
    assert 'icemac.addressbook.keyword.KeywordContainer' in browser.contents
    # base class of context
    assert 'zope.container.btree.BTreeContainer' in browser.contents
    # an interface of context
    assert 'icemac.addressbook.interfaces.IKeywords' in browser.contents


def test_inspector__Inspector__show_context__3(address_book, browser):
    """It renders context information on a the root object."""
    browser.login('globalmgr')
    browser.open(browser.INSPECTOR_ROOT_OBJECT_URL)
    # the base classes of the root object
    assert (
        "(&lt;class 'zope.container.folder.Folder'&gt;, "
        "&lt;class 'zope.site.site.SiteManagerContainer'&gt;)" in
        browser.contents)
    # an interface of the root object
    assert 'zope.container.interfaces.IContainer' in browser.contents


@pytest.mark.parametrize('username', ('editor', 'visitor', 'mgr', 'archivist'))
def test_inspector__Inspector__1(address_book, browser, username):
    """It cannot be accessed by non-global-admin users on a view."""
    browser.login(username)
    browser.assert_forbidden(browser.INSPECTOR_VIEW_URL)


@pytest.mark.parametrize('username', ('editor', 'visitor', 'mgr', 'archivist'))
def test_inspector__Inspector__2(address_book, browser, username):
    """It cannot be accessed by non-global-admin users on an object."""
    browser.login(username)
    browser.assert_forbidden(browser.INSPECTOR_OBJECT_URL)


@pytest.mark.parametrize('username', ('editor', 'visitor', 'mgr', 'archivist'))
def test_inspector__Inspector__3(address_book, browser, username):
    """It cannot be accessed by non-global-admin users on the root object."""
    browser.login(username)
    browser.assert_forbidden(browser.INSPECTOR_ROOT_OBJECT_URL)

from icemac.addressbook.browser.search.result.handler.manager import (
    SearchResultHandler)


def makeSRHandler(viewName):
    """Create a `SearchResultHandler` with the specified `viewName`."""
    handler = SearchResultHandler(None, None, None, None)
    handler.viewName = viewName
    return handler


def test_manager__SearchResultHandler___eq___1():
    """SearchResultHandler instances are equal when `viewName` is equal."""
    assert makeSRHandler('@@asdf.html') == makeSRHandler('@@asdf.html')


def test_manager__SearchResultHandler___eq___2():
    """SearchResultHandler instances are not equal with unequal `viewName`."""
    # There is no __neq__ implemented!
    assert not(makeSRHandler('@@foo.html') == makeSRHandler('@@bar.html'))


def test_manager__SearchResultHandler___eq___3():
    """A SearchResultHandler instance is not equal to anything else."""
    # There is no __neq__ implemented!
    assert not(makeSRHandler(None) == object())

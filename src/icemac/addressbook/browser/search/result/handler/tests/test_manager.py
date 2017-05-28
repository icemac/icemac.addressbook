from icemac.addressbook.browser.search.result.handler.manager import (
    SearchResultHandler)


def makeSRHandler(viewName):
    """Create a `SearchResultHandler` with the specified `viewName`."""
    handler = SearchResultHandler(None, None, None, None)
    handler.viewName = viewName
    return handler


def test_manager__SearchResultHandler____eq____1():
    """It is equal when `viewName` is equal."""
    assert makeSRHandler('@@asdf.html') == makeSRHandler('@@asdf.html')


def test_manager__SearchResultHandler____eq____2():
    """It is not equal with unequal `viewName`."""
    # There is no __neq__ implemented!
    assert not(makeSRHandler('@@foo.html') == makeSRHandler('@@bar.html'))


def test_manager__SearchResultHandler____eq____3():
    """It is not equal to anything else."""
    # There is no __neq__ implemented!
    assert not(makeSRHandler(None) == object())

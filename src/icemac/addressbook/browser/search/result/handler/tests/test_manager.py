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


def test_manager__SearchResultHandler____hash____1():
    """It is hashable.

    It is only needed for Python 3 where classes having an __eq__ method do
    not have a __hash__ method.
    """
    assert hash(makeSRHandler(None)) is not None

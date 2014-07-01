import unittest


class TestSearchResultHandler(unittest.TestCase):
    """Testing .manager.SearchResultHandler."""

    def test_two_SearchResultHandlers_are_equal_when_viewName_is_equal(self):
        from icemac.addressbook.browser.search.result.handler.manager import (
            SearchResultHandler)
        h1 = SearchResultHandler(None, None, None, None)
        h1.viewName = '@@asdf.html'
        h2 = SearchResultHandler(None, None, None, None)
        h2.viewName = '@@asdf.html'
        self.assertEqual(h1, h2)

    def test_two_SearchResultHandlers_are_not_equal_when_viewName_is_unequal(
            self):
        from icemac.addressbook.browser.search.result.handler.manager import (
            SearchResultHandler)
        h1 = SearchResultHandler(None, None, None, None)
        h1.viewName = '@@foo.html'
        h2 = SearchResultHandler(None, None, None, None)
        h2.viewName = '@@bar.html'
        self.assertFalse(h1 == h2)

    def test_SearchResultHandler_is_not_equal_to_any_thing_else(self):
        from icemac.addressbook.browser.search.result.handler.manager import (
            SearchResultHandler)
        h1 = SearchResultHandler(None, None, None, None)
        self.assertFalse(h1 == object())

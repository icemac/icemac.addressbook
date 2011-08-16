import unittest2 as unittest


class TestOnlyAdminIsAllowedToUseUpdate(unittest.TestCase):

    def test_editor_is_not_able_to_see_update_search_result_handler(self):
        self.fail('nyi')

    def test_editor_is_not_able_to_access_update_search_result_handler(self):
        # even though he knows the url
        self.fail('nyi')

    def test_visitor_is_not_able_to_see_update_search_result_handler(self):
        self.fail('nyi')

    def test_visitor_is_not_able_to_access_update_search_result_handler(self):
        # even though he knows the url
        self.fail('nyi')

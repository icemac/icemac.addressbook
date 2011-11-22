# -*- coding: utf-8 -*-
# Copyright (c) 2011 Michael Howitz
# See also LICENSE.txt
import icemac.addressbook.browser.testing
import unittest2 as unittest
import urllib2


class TestOnlyAdminIsAllowedToUseUpdate(unittest.TestCase):

    layer = icemac.addressbook.browser.testing.WSGI_SEARCH_LAYER

    def _get_browser(self, username):
        import icemac.addressbook.testing
        browser = icemac.addressbook.testing.Browser()
        browser.login(username)
        return browser

    def update_handler_is_not_visible_for(self, username):
        browser = self._get_browser(username)
        browser.open('http://localhost/ab/@@multi_keyword.html')
        browser.getControl('keywords').displayValue = ['church']
        browser.getControl('Search').click()
        self.assertEqual(
            ['XLS export main (Exports person data and main addresses resp. '
              'phone numbers.)',
             'XLS export complete (Exports person data and all addresses '
               'resp. phone numbers.)',
             'E-Mail (Creates a link to send e-mails.)'],
            browser.getControl('Apply on selected persons').displayOptions)

    def each_part_of_the_update_wizard_is_not_accessible_for(self, username):
        browser = self._get_browser(username)
        for url in ('http://localhost/ab/@@multi-update',
                    'http://localhost/ab/multi-update/enterValue',
                    'http://localhost/ab/multi-update/checkResult',
                    'http://localhost/ab/@@multi-update-completed'):
            self._assert_access_raises_forbidden(browser, url)

    def _assert_access_raises_forbidden(self, browser, url):
        with self.assertRaises(urllib2.HTTPError) as err:
            browser.open(url)
        self.assertEqual('HTTP Error 403: Forbidden', str(err.exception))

    # Tests

    def test_editor_is_not_able_to_see_update_search_result_handler(self):
        self.update_handler_is_not_visible_for('editor')

    def test_editor_is_not_able_to_access_update_search_result_handler(self):
        # even though he knows the url
        self.each_part_of_the_update_wizard_is_not_accessible_for('editor')

    def test_visitor_is_not_able_to_see_update_search_result_handler(self):
        self.update_handler_is_not_visible_for('visitor')

    def test_visitor_is_not_able_to_access_update_search_result_handler(self):
        # even though he knows the url
        self.each_part_of_the_update_wizard_is_not_accessible_for('visitor')

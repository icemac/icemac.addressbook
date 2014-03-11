# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import icemac.addressbook.testing


class OverviewTests(icemac.addressbook.testing.BrowserTestCase):
    """Testing ..principals.Overview."""

    def test_roles_are_listed_comma_separated(self):
        ab = self.layer['addressbook']
        icemac.addressbook.testing.create_user(
            ab, ab, 'Hans', 'Tester', 'tester@example.com', 'secret',
            ['Visitor', 'Editor'])
        browser = self.get_browser('mgr')
        browser.open('http://localhost/ab/++attribute++principals')
        self.assertEqual(
            ['Editor, Visitor'],
            browser.etree.xpath('//tr/td[3]/text()'))

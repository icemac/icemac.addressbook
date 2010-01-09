# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.keyword
import icemac.addressbook.testing
import unittest


class TestKeywords(unittest.TestCase):

    def setUp(self):
        self.keywords = icemac.addressbook.keyword.KeywordContainer()

    def test_get_keywords_empty(self):
        self.assertEqual([], self.keywords.get_keywords())

    def test_get_keywords_not_empty(self):
        self.keywords['1'] = icemac.addressbook.keyword.Keyword(u'qwe')
        self.keywords['2'] = icemac.addressbook.keyword.Keyword(u'asd')
        self.keywords['3'] = icemac.addressbook.keyword.Keyword(u'dfg')
        self.keywords['4'] = icemac.addressbook.keyword.Keyword(u'bgr')
        self.assertEqual(['asd', 'bgr', 'dfg', 'qwe'],
                         [x.title for x in self.keywords.get_keywords()])

    def test_get_keyword_by_title_found(self):
        self.keywords['1'] = icemac.addressbook.keyword.Keyword(u'foo')
        self.keywords['2'] = icemac.addressbook.keyword.Keyword(u'bar')
        self.assertEqual(self.keywords['1'],
                         self.keywords.get_keyword_by_title(u'foo'))
        self.assertEqual(self.keywords['2'],
                         self.keywords.get_keyword_by_title(u'bar'))

    def test_get_keyword_by_title_empty_container(self):
        self.assertEqual(None, self.keywords.get_keyword_by_title(u'asdf'))

    def test_get_keyword_by_title_not_found(self):
        self.keywords['1'] = icemac.addressbook.keyword.Keyword(u'asdf')
        self.assertEqual(None, self.keywords.get_keyword_by_title(u'foo'))
        self.assertEqual(None, self.keywords.get_keyword_by_title(u'bar'))

    def test_get_keyword_by_title_not_found_default(self):
        self.keywords['1'] = icemac.addressbook.keyword.Keyword(u'asdf')
        self.assertEqual('baz',
                         self.keywords.get_keyword_by_title(u'foo', 'baz'))


def test_suite():
    return icemac.addressbook.testing.UnittestSuite(TestKeywords)


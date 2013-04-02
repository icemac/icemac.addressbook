# -*- coding: utf-8 -*-
# Copyright (c) 2009-2013 Michael Howitz
# See also LICENSE.txt

import StringIO
import doctest
import logging
import sys
import zc.buildout.testing


def DocFileSuite(*args, **kw):

    def setUp(test):
        zc.buildout.testing.buildoutSetUp(test)
        zc.buildout.testing.install_develop('icemac.addressbook', test)

    def tearDown(test):
        zc.buildout.testing.buildoutTearDown(test)

    def call_with_user_input(input, function, *args, **kw):
        stdin = StringIO.StringIO()
        stdin.write(input)
        stdin.seek(0)
        _orig_stdin = sys.stdin
        try:
            sys.stdin = stdin
            return function(*args, **kw)
        finally:
            sys.stdin = _orig_stdin

    kw['setUp'] = setUp
    kw['tearDown'] = tearDown
    kw['optionflags'] = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
    kw['globs'] = dict(call_with_user_input=call_with_user_input)
    return doctest.DocFileSuite(*args, **kw)


def test_suite():
    return DocFileSuite('../install.txt')

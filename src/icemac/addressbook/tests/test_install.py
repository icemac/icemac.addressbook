# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

import StringIO
import doctest
import logging
import sys
import zc.buildout.testing
import zope.testing.doctest


def DocFileSuite(*args, **kw):

    def setUp(test):
        # XXX needed until zc.buildout 1.2.2 is released
        test.original_logging_handlers = logging.getLogger().handlers[:]
        # XXX end
        zc.buildout.testing.buildoutSetUp(test)
        zc.buildout.testing.install_develop('icemac.addressbook', test)

    def tearDown(test):
        zc.buildout.testing.buildoutTearDown(test)
        # XXX needed until zc.buildout 1.2.2 is released
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        for handler in test.original_logging_handlers:
            root_logger.addHandler(handler)
        # XXX end

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
    return zope.testing.doctest.DocFileSuite(*args, **kw)

def test_suite():
    return DocFileSuite('../install.txt')

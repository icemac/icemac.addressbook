# -*- coding: utf-8 -*-
# Copyright (c) 2009-2013 Michael Howitz
# See also LICENSE.txt
import StringIO
import doctest
import os
import shutil
import sys
import sys
import tempfile
import unittest
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


class TestNotMatchedPrerequisites(unittest.TestCase):
    """Testing ..install.not_matched_prerequisites().

    This function tests whether the installation might be successful.
    """

    def setUp(self):
        super(TestNotMatchedPrerequisites, self).setUp()
        self.tempdir = tempfile.mkdtemp()
        self._old_cwd = os.getcwd()
        os.chdir(self.tempdir)

    def tearDown(self):
        super(TestNotMatchedPrerequisites, self).tearDown()
        shutil.rmtree(self.tempdir)
        os.chdir(self._old_cwd)

    def not_matched_prerequisites(self):
        from ..install import not_matched_prerequisites
        return not_matched_prerequisites()

    def test_returns_error_text_if_buildout_cfg_exists_in_cwd(self):
        with open('buildout.cfg', 'w') as buildout_cfg:
            buildout_cfg.write('[buildout]')
        self.assertEqual(
            'ERROR: buildout.cfg already exists.\n'
            '       Please (re-)move the existing one and restart install.',
            self.not_matched_prerequisites())

    def test_returns_False_if_no_buildout_cfg_exists_in_cwd(self):
        self.assertFalse(self.not_matched_prerequisites())

    # icemac.addressbook currently only runs with some Python
    # versions. If another version is used, an error message is returned.

    def test_returns_error_text_for_too_old_python_version(self):
        orig_version_info = sys.version_info
        try:
            sys.version_info = (2, 5, 6, 'final', 0)
            self.assertEqual(
                'ERROR: icemac.addressbook currently supports only Python 2.7.'
                '\n       But you try to install it using Python 2.5.6.',
                self.not_matched_prerequisites())
        finally:
            sys.version_info = orig_version_info

    def test_returns_error_text_for_too_new_python_version(self):
        orig_version_info = sys.version_info
        try:
            sys.version_info = (3, 0, 0, 'final', 0)
            self.assertEqual(
                'ERROR: icemac.addressbook currently supports only Python 2.7.'
                '\n       But you try to install it using Python 3.0.0.',
                self.not_matched_prerequisites())
        finally:
            sys.version_info = orig_version_info

    def test_returns_False_on_right_python_version(self):
        # We expect that the version of the python which runs the tests
        # matches the requirement, so ``False`` is returned:
        self.assertFalse(self.not_matched_prerequisites())


def test_suite():
    return unittest.TestSuite(
        [DocFileSuite('../install.txt'),
         unittest.makeSuite(TestNotMatchedPrerequisites)])

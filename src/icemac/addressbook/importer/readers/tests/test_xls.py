# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.importer.readers.testing
import icemac.addressbook.importer.readers.xls


class TestXLS(icemac.addressbook.importer.readers.testing.BaseReaderTest):

    reader_class = icemac.addressbook.importer.readers.xls.XLSReader
    import_file = 'xls_default.xls'
    import_file_short = 'xls_short.xls'


def test_suite():
    return icemac.addressbook.testing.UnittestSuite(TestXLS)

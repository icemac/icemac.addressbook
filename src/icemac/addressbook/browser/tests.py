# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id$

import icemac.addressbook.testing
import zope.testing.renormalizing

def test_suite():
    suite = icemac.addressbook.testing.FunctionalDocFileSuite(
        "browser/addressbook/addressbook.txt",
        "browser/authentication/login.txt",
        "browser/entities/bugfix.txt",
        "browser/entities/delete_choice_value.txt",
        "browser/entities/entities.txt",
        "browser/entities/file.txt",
        "browser/export/export.txt",
        "browser/export/translation.txt",
        "browser/export/userfields.txt",
        "browser/keyword/keyword.txt",
        "browser/masterdata/masterdata.txt",
        "browser/person/clone.txt",
        "browser/person/file.txt",
        "browser/person/person.txt",
        "browser/person/translation.txt",
        "browser/principals/principals.txt",
        "browser/rootfolder/rootfolder.txt",
        "browser/search/search.txt",
        )
    suite.addTest(
        icemac.addressbook.testing.FunctionalDocFileSuite(
            # Tests which do not need the default <DATETIME> normalizer:
            "browser/metadata.txt",
            checker=zope.testing.renormalizing.RENormalizing([])
            ))
    return suite


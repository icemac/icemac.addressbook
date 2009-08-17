# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import zope.container.btree
import zope.interface
import icemac.addressbook.importer.interfaces


class Importer(zope.container.btree.BTreeContainer):
    "Importer containing files for import."
    zope.interface.implements(
        icemac.addressbook.importer.interfaces.IImporter)

    file_marker_interface = icemac.addressbook.importer.interfaces.IImportFile

# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.importer.interfaces
import zc.sourcefactory.contextual
import zope.interface
import zope.security.proxy

class BaseReader(object):
    """Base reader for import files."""

    zope.interface.implements(
        icemac.addressbook.importer.interfaces.IImportFileReader)
    zope.component.adapts(None)

    file = None

    def __init__(self, ignored=None):
        """Adapter look-up requires an argument"""

    @classmethod
    def open(cls, file_handle):
        reader = cls()
        reader.file = file_handle
        return reader

    @classmethod
    def canRead(cls, file_handle):
        try:
            reader = cls.open(file_handle)
            reader.getFieldNames()
        except:
            return False
        return True

    def __del__(self):
        if self.file is not None:
            self.file.close()


def _get_file_handle(blob):
    """Get a file handle to a blob object."""
    file_handle = blob.openDetached()
    file_handle = zope.security.proxy.removeSecurityProxy(file_handle)
    return file_handle


class Source(zc.sourcefactory.contextual.BasicContextualSourceFactory):
    """Source of registered readers."""

    def getValues(self, context):
        adapters =  zope.component.getAdapters(
            (None, ), icemac.addressbook.importer.interfaces.IImportFileReader)

        for name, adapter in adapters:
            if adapter.__class__.canRead(_get_file_handle(context)):
                yield name

    def getTitle(self, context, value):
        adapter = zope.component.getAdapter(
            None, icemac.addressbook.importer.interfaces.IImportFileReader,
            name=value)

        return adapter.title

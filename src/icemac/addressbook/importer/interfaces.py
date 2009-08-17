# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import zope.interface
import zope.schema


class IImporter(zope.interface.Interface):
    """Importer and storage for import files."""

    file_marker_interface = zope.interface.Attribute(
        u"""Interface to be used as marker interface for contained files.""")


class IImportFileContainer(zope.interface.Interface):
    "Marker interface for container which can contain files."


class IImportFile(zope.interface.Interface):
    """Marker interface for import files."""


class IImportFileReader(zope.interface.Interface):
    """Reader for an import file.

    Text fields are returned as unicode strings.
    Date fields are returned as ISO date strings.

    """

    title = zope.schema.TextLine(
        title=u"User understandable name of the reader.", readonly=True)

    def canRead(file_handle):
        """Tell whether this reader is able to read the given file.

        Class method!
        """

    def open(file_handle):
        """Create a new file reader and use `file_handle` to read from."""

    def getFieldNames():
        """Get an iterable of the names of the fields in the file.

        The names are unicode strings.

        """

    def getFieldSamples(field_name):
        """Get an iterable of sample values for a field.

        The values are unicode strings.

        """

    def __iter__():
        """Iterate over the file.

        Yields a dict mapping field name to value for each line in the file.
        The keys and values in the dict are unicode strings.

        """

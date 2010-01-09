# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

import zope.interface

class IExporter(zope.interface.Interface):
    """Exporting facility."""

    title = zope.interface.Attribute(u'Title of the exporter.')
    description = zope.interface.Attribute(
        u'Short description of the exporter.')
    file_extension = zope.interface.Attribute(
        u'Extension (without the leading dot!) to be set on export file name.')
    mime_type = zope.interface.Attribute(u'Mime-type of the export file.')

    def export():
        """Export to a file.

        Returns a file or file-like-object.

        """

    def __eq__(other):
        """Checks whether two instances have the same class."""

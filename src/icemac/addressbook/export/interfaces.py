import zope.interface


class IExporter(zope.interface.Interface):
    """Exporting facility."""

    file_extension = zope.interface.Attribute(
        u'Extension (without the leading dot!) to be set on export file name.')
    mime_type = zope.interface.Attribute(u'Mime-type of the export file.')

    def export():
        """Export to a file.

        Returns a file or file-like-object.

        """

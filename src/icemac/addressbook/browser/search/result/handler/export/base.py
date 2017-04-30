import icemac.addressbook.browser.search.result.handler.base


class BaseExport(icemac.addressbook.browser.search.result.handler.base.Base):
    """Base class for exporters.

    Subclasses only have to set the `exporter_class` which should implement
    the interface `icemac.addressbook.export.interfaces.IExporter`.
    """

    exporter_class = NotImplemented

    def __call__(self):
        exporter = self.exporter_class(self.persons, self.request)

        self.request.response.setHeader('Content-Type', exporter.mime_type)
        self.request.response.setHeader(
            'Content-Disposition',
            'attachment; filename=addressbook_export.%s' % (
                exporter.file_extension))

        return exporter.export()

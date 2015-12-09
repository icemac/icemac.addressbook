from icemac.addressbook.browser.search.result.handler.export.base import (
    BaseExport)
import icemac.addressbook.export.xls.simple


class DefaultsExport(BaseExport):
    """Exporter for default data and addresses."""

    exporter_class = icemac.addressbook.export.xls.simple.DefaultsExport


class CompleteExport(BaseExport):
    """Exporter for all data and addresses."""

    exporter_class = icemac.addressbook.export.xls.simple.CompleteExport

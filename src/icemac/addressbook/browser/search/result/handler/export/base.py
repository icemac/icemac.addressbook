# -*- coding: utf-8 -*-
# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
import icemac.addressbook.browser.base
import icemac.addressbook.browser.search.base
import icemac.addressbook.interfaces


class BaseExport(object):
    """Base class for exporters.

    Subclasses only have to set the `exporter_class` which should implement
    the interface `icemac.addressbook.export.interfaces.IExporter`.

    """
    exporter_class = NotImplemented

    def __call__(self):
        session = icemac.addressbook.browser.base.get_session(self.request)
        persons = [self.context[id] for id in session['person_ids']]
        exporter = self.exporter_class(persons, self.request)

        self.request.response.setHeader('Content-Type', exporter.mime_type)
        self.request.response.setHeader(
            'Content-Disposition',
            'attachment; filename=addressbook_export.%s' % (
                exporter.file_extension))

        return exporter.export()

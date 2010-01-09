# -*- coding: utf-8 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id$

import zope.session.interfaces

import icemac.addressbook.interfaces


class SimpleExport(object):

    def __call__(self):
        session = zope.session.interfaces.ISession(self.request)[
            icemac.addressbook.interfaces.PACKAGE_ID]
        persons = [self.context[id] for id in session['person_ids']]
        exporter = zope.component.getMultiAdapter(
            (persons, self.request),
            icemac.addressbook.export.interfaces.IExporter,
            name=session['exporter_token'])

        self.request.response.setHeader('Content-Type', exporter.mime_type)
        self.request.response.setHeader(
            'Content-Disposition',
            'attachment; filename=addressbook_export.%s' % (
                exporter.file_extension))

        return exporter.export()

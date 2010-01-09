# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.export.interfaces
import zc.sourcefactory.basic
import zc.sourcefactory.contextual
import zc.sourcefactory.interfaces
import zope.component
import zope.interface
import zope.publisher.browser


def get_exporter_tuples():
    """Get (name, instance) tuples of the registered exporters."""
    return zope.component.getAdapters(
        ([], zope.publisher.browser.TestRequest()),
        icemac.addressbook.export.interfaces.IExporter)


@zope.component.adapter(icemac.addressbook.export.interfaces.IExporter)
@zope.interface.implementer(zc.sourcefactory.interfaces.IToken)
def fromExporter(value):
    """The token must be the name for which the adapter is registered, so the
    adapter can be looked up later using this token."""
    for name, exporter in get_exporter_tuples():
        if value == exporter:
            return name


class ExporterSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        for name, value in get_exporter_tuples():
            yield value

    def getTitle(self, value):
        return _(u'${title} (${desc})',
                 mapping=dict(title=value.title, desc=value.description))

exporter_source = ExporterSource()

# -*- coding: utf-8 -*-
# Copyright (c) 2010 Michael Howitz
# See also LICENSE.txt

import zope.component
import zope.publisher.interfaces.browser
import zope.interface
import icemac.addressbook.export.interfaces


class BaseExporter(object):
    "Abstract base class for exporters which defines some convenience methods."

    zope.component.adapts(list,
                          zope.publisher.interfaces.browser.IBrowserRequest)
    zope.interface.implements(icemac.addressbook.export.interfaces.IExporter)

    # to be set in subclass
    file_extension = None
    mime_type = None
    title = None
    description = None

    def __init__(self, persons, request=None):
        self.persons = persons
        self.request = request

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def export(self):
        raise NotImplementedError()

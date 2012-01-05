# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Michael Howitz
# See also LICENSE.txt

import zope.interface
import icemac.addressbook.export.interfaces


class BaseExporter(object):
    "Abstract base class for exporters which defines some convenience methods."

    zope.interface.implements(icemac.addressbook.export.interfaces.IExporter)

    # to be set in subclass
    file_extension = NotImplemented
    mime_type = NotImplemented

    def __init__(self, persons, request=None):
        self.persons = persons
        self.request = request

    def export(self):
        raise NotImplementedError()

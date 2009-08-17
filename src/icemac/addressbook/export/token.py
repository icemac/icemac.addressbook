# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

import zc.sourcefactory.interfaces
import zope.component
import zope.interface

import icemac.addressbook.export.interfaces

@zope.component.adapter(icemac.addressbook.export.interfaces.IExporter)
@zope.interface.implementer(zc.sourcefactory.interfaces.IToken)
def fromExporter(value):
    "Exporters are global utilities, the existing token adapters do not work."
    return "%s.%s" % (value.__module__, value.__class__.__name__)

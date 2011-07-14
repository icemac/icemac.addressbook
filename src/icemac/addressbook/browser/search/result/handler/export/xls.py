# -*- coding: utf-8 -*-
# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import _
import icemac.addressbook.browser.search.result.handler.export.base
import icemac.addressbook.export.xls.simple
import icemac.addressbook.interfaces
import zope.session.interfaces


class DefaultsExport(
    icemac.addressbook.browser.search.result.handler.export.base.BaseExport):
    """Exporter for default data and addresses."""

    exporter_class = icemac.addressbook.export.xls.simple.DefaultsExport


class CompleteExport(
    icemac.addressbook.browser.search.result.handler.export.base.BaseExport):
    """Exporter for all data and addresses."""

    exporter_class = icemac.addressbook.export.xls.simple.CompleteExport

# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Michael Howitz
# See also LICENSE.txt
# $Id$

import icemac.addressbook.browser.search.result.handler.export.base
import icemac.addressbook.export.xls.simple


class DefaultsExport(
    icemac.addressbook.browser.search.result.handler.export.base.BaseExport):
    """Exporter for default data and addresses."""

    exporter_class = icemac.addressbook.export.xls.simple.DefaultsExport


class CompleteExport(
    icemac.addressbook.browser.search.result.handler.export.base.BaseExport):
    """Exporter for all data and addresses."""

    exporter_class = icemac.addressbook.export.xls.simple.CompleteExport

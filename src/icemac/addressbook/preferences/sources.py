# -*- coding: utf-8 -*-
# Copyright (c) 2010 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import _
import icemac.addressbook.sources
import stabledict
import zc.sourcefactory.basic


class ColumnSource(zc.sourcefactory.basic.BasicSourceFactory):
    "Columns in the person list."

    def getValues(self):
        # XXX see i.a.importer.sources
        return ['name', 'birthdate']

column_source = ColumnSource()


class AscDescSource(icemac.addressbook.sources.TitleMappingSource):
    _mapping = stabledict.StableDict(
        (('asc', _(u'ascending (A-->Z)')),
         ('desc', _(u'descending (Z-->A)'))))

asc_des_csource = AscDescSource()

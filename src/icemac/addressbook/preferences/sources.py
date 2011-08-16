# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import _
import icemac.addressbook.interfaces
import icemac.addressbook.sources
import stabledict
import zc.sourcefactory.basic
import zope.component

# BBB
from icemac.addressbook.fieldsource import tokenize, untokenize
from icemac.addressbook.fieldsource import source as column_source


class AscDescSource(icemac.addressbook.sources.TitleMappingSource):
    _mapping = stabledict.StableDict(
        (('ascending', _(u'ascending (A-->Z)')),
         ('descending', _(u'descending (Z-->A)'))))

asc_des_csource = AscDescSource()

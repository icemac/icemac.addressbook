# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import stabledict
import zc.sourcefactory.basic
import zc.sourcefactory.contextual
import zope.component


class TitleMappingSource(zc.sourcefactory.basic.BasicSourceFactory):
    "Abstract base class for sources using a mapping between value and title."

    _mapping = None  # to be set in child class

    def getValues(self):
        return self._mapping.keys()

    def getTitle(self, value):
        return self._mapping[value]


class YesNoSource(TitleMappingSource):
    _mapping = stabledict.StableDict(
        ((True, _(u'yes')),
         (False, _(u'no'))))

yes_no_source = YesNoSource()


class FieldTypeSource(TitleMappingSource):
    _mapping = stabledict.StableDict(
        ((u'Bool', _(u'bool')),
         (u'Choice', _('choice')),
         (u'Date', _(u'date')),
         (u'Datetime', _(u'datetime')),
         (u'Decimal', _('decimal number')),
         (u'Int', _(u'integer number')),
         (u'Text', _(u'text area')),
         (u'TextLine', _(u'text line')),
         (u'URI', _(u'URL')),
         ))


class KeywordSource(zc.sourcefactory.basic.BasicSourceFactory):
    "Source of keywords in the address book."

    def getValues(self):
        import icemac.addressbook.interfaces  # avoid circular import
        keywords = zope.component.getUtility(
            icemac.addressbook.interfaces.IKeywords)
        return sorted(keywords.get_keywords(), key=lambda x: x.title.lower())

    def getTitle(self, value):
        return value.title

keyword_source = KeywordSource()


class ContextByInterfaceSource(
    zc.sourcefactory.contextual.BasicContextualSourceFactory):
    "Source to select objects from context container by a given interface."

    def __init__(self, interface):
        super(ContextByInterfaceSource, self).__init__()
        self.interface = interface

    def getValues(self, context):
        for value in context.values():
            if self.interface.providedBy(value):
                yield value

    def getTitle(self, context, value):
        import icemac.addressbook.interfaces  # avoid circular import
        return icemac.addressbook.interfaces.ITitle(value)

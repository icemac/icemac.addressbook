# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

import stabledict
import zc.sourcefactory.basic
import zc.sourcefactory.contextual
import zope.component

import icemac.addressbook.export.interfaces

from icemac.addressbook.i18n import MessageFactory as _


class TitleMappingSource(zc.sourcefactory.basic.BasicSourceFactory):
    "Abstract base class for sources using a mapping between value and title."
    
    _mapping = None # to be set in child class

    def getValues(self):
        return self._mapping.keys()

    def getTitle(self, value):
        return self._mapping[value]


class SexSource(TitleMappingSource):
    _mapping = stabledict.StableDict(
        ((u'male', _(u'male')),
         (u'female', _(u'female'))))


class SalutationSource(TitleMappingSource):
    _mapping = stabledict.StableDict(
        ((u'male', _(u'Mr.')), 
         (u'female', _(u'Ms.'))))

salutation_source = SalutationSource()


class PhoneNumberKindSource(TitleMappingSource):
    _mapping = stabledict.StableDict((
            (u'cell phone', _(u'cell phone')),
            (u'private fax', _(u'private fax')),
            (u'private phone', _(u'private phone')),
            (u'work fax', _(u'work fax')),
            (u'work phone', _(u'work phone')),
            (u'other', _(u'other')),
            ))

phone_number_kind_source = PhoneNumberKindSource()


class WorkPrivateKindSource(TitleMappingSource):
    _mapping = stabledict.StableDict(
        ((u'private', _(u'private')),
         (u'work', _(u'work')),
         (u'other', _(u'other'))))


work_private_kind_source = WorkPrivateKindSource()


class KeywordSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        import icemac.addressbook.interfaces # avoid circular import
        keywords = zope.component.getUtility(
            icemac.addressbook.interfaces.IKeywords)
        return keywords.get_keywords()

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
        import icemac.addressbook.interfaces # avoid circular import
        return icemac.addressbook.interfaces.ITitle(value)


class ExporterSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return zope.component.getAllUtilitiesRegisteredFor(
            icemac.addressbook.export.interfaces.IExporter)

    def getTitle(self, value):
        return u'%s (%s)' % (value.title, value.description)

exporter_source = ExporterSource()

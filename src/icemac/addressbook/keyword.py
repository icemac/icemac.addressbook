# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id$

import persistent
import zope.catalog.interfaces
import zope.container.btree
import zope.container.contained
import zope.component
import zope.interface
import zope.lifecycleevent
import zope.schema.fieldproperty

import icemac.addressbook.interfaces

from icemac.addressbook.i18n import MessageFactory as _


class KeywordContainer(zope.container.btree.BTreeContainer):
    "A container for keywords."
    zope.interface.implements(icemac.addressbook.interfaces.IKeywords)

    def get_keywords(self):
        # sorting will be done in presentation layer
        return self.values()

    def get_keyword_by_title(self, title, default=None):
        for keyword in self.values():
            if keyword.title == title:
                return keyword
        return default


class Keyword(persistent.Persistent, zope.container.contained.Contained):
    "A keyword."
    zope.interface.implements(icemac.addressbook.interfaces.IKeyword)

    def __init__(self, title=None):
        super(Keyword, self).__init__()
        if title is not None:
            self.title = title

    title = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IKeyword['title'])


keyword_entity = icemac.addressbook.entities.create_entity(
    _(u'keyword'), icemac.addressbook.interfaces.IKeyword, Keyword)


@zope.component.adapter(icemac.addressbook.interfaces.IKeyword,
                        zope.lifecycleevent.IObjectModifiedEvent)
def changed(obj, event):
    for desc in event.descriptions:
        if (desc.interface == icemac.addressbook.interfaces.IKeyword and
            'title' in desc.attributes):
            catalog = zope.component.getUtility(
                zope.catalog.interfaces.ICatalog)
            catalog.updateIndex(catalog.get('keywords'))
            break


def uniqueTitles(obj, event):
    if getattr(obj, '__parent__', None) is None:
        return
    container = obj.__parent__
    titles = [x.title for x in container.values()]
    if len(titles) != len(set(titles)):
        raise zope.interface.Invalid(_(u'This keyword already exists.'))

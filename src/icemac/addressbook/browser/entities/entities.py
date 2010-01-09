# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.browser.table
import icemac.addressbook.interfaces
import z3c.table.column
import zope.container.traversal
import zope.location
import zope.publisher.interfaces.http
import zope.security.proxy
import zope.traversing.browser.absoluteurl


class List(icemac.addressbook.browser.table.Table):
    """List existing entities."""

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, z3c.table.column.I18nGetAttrColumn, 'title', weight=1,
                header=_(u'Entity'), attrName='title'),
            z3c.table.column.addColumn(
                self, z3c.table.column.LinkColumn, 'fields', weight=200,
                header=u'', linkContent=_(u'Edit fields')),
            ]

    @property
    def values(self):
        # Need to remove security otherwise local administrators get
        # an unauthorized exception.
        for x in self.context.getAllEntities():
            yield zope.security.proxy.getObject(x)


class EntityAbsoluteURL(zope.traversing.browser.absoluteurl.AbsoluteURL):
    """AbsoluteURL adapter for an entity."""

    zope.component.adapts(icemac.addressbook.interfaces.IEntity,
                          zope.publisher.interfaces.http.IHTTPRequest)

    def __str__(self):
        # parent is the entities utility and name is the class name
        parent = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntities)
        url = str(zope.component.getMultiAdapter(
            (parent, self.request),
            zope.traversing.browser.interfaces.IAbsoluteURL))
        url += '/' + self.context.class_name
        return url


class EntitiesTraverser(zope.container.traversal.ItemTraverser):

    zope.interface.implementsOnly(zope.publisher.interfaces.IPublishTraverse)
    zope.component.adapts(icemac.addressbook.interfaces.IEntities,
                          zope.publisher.interfaces.http.IHTTPRequest)

    def publishTraverse(self, request, name):
        entity = zope.component.queryUtility(
            icemac.addressbook.interfaces.IEntity, name=name)
        if entity is not None:
            return zope.location.LocationProxy(entity, self.context, name)
        return super(EntitiesTraverser, self).publishTraverse(request, name)

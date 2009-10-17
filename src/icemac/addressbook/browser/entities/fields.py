# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.browser.table
import icemac.addressbook.entities
import icemac.addressbook.interfaces
import persistent
import z3c.table.column
import zope.app.publication.traversers
import zope.publisher.interfaces
import zope.publisher.interfaces.http
import zope.publisher.interfaces.http
import zope.security.proxy
import zope.traversing.browser.interfaces


class FieldsTraverser(
    zope.app.publication.traversers.SimpleComponentTraverser):

    zope.interface.implementsOnly(zope.publisher.interfaces.IPublishTraverse)
    zope.component.adapts(icemac.addressbook.interfaces.IEntity,
                          zope.publisher.interfaces.http.IHTTPRequest)

    def publishTraverse(self, request, name):
        entities = zope.component.queryUtility(
            icemac.addressbook.interfaces.IEntities)
        try:
            return entities[name]
        except KeyError:
            return super(FieldsTraverser, self).publishTraverse(request, name)


class LinkColumn(z3c.table.column.LinkColumn):

    def getLinkURL(self, item):
        entities = icemac.addressbook.browser.base.get_entities_util()
        url = zope.component.getMultiAdapter(
            (entities, self.request),
            zope.traversing.browser.interfaces.IAbsoluteURL)()
        url += "/" + self.context.__name__ + "/" + item.__name__
        return url

    def renderCell(self, item):
        if icemac.addressbook.interfaces.IField.providedBy(item):
            return super(LinkColumn, self).renderCell(item)
        return ''


class List(icemac.addressbook.browser.table.Table):
    """List fields of an entity."""

    sortOn = None # do not sort

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, z3c.table.column.GetAttrColumn, 'title', weight=1,
                header=_(u'Field'), attrName='title'),
            z3c.table.column.addColumn(
                self, LinkColumn, 'edit', weight=200,
                header=_(u''), linkContent=_(u'Edit')),
            ]

    @property
    def values(self):
        # zope.schema fields are no content classes, so they have no
        # permissions defined
        return [zope.security.proxy.getObject(field)
                for name, field in self.context.getRawFields()]


class FieldAdapterFactory(persistent.Persistent):

    def __init__(self, field):
        self._field = field

    def __call__(self, *args):
        return self._field


class AddForm(icemac.addressbook.browser.base.BaseAddForm):

    class_ = icemac.addressbook.entities.Field
    interface = icemac.addressbook.interfaces.IField
    next_url = 'parent'

    def add(self, obj):
        parent = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntities)
        self._name = icemac.addressbook.utils.add(parent, obj)
        # register as adapter
        sm = zope.site.hooks.getSiteManager()
        sm.registerAdapter(
            FieldAdapterFactory(obj),
            provided=icemac.addressbook.interfaces.IField,
            required=(icemac.addressbook.interfaces.IEntity,
                      zope.security.proxy.getObject(self.context.interface)),
            name=self._name)


class EditForm(icemac.addressbook.browser.base.BaseEditForm):

    interface = icemac.addressbook.interfaces.IField

    def redirect_to_next_url(self, *args):
        # redirect to the entity
        self.request.response.redirect(self.request.URL.get(-2))

# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.browser.metadata
import icemac.addressbook.browser.table
import icemac.addressbook.entities
import icemac.addressbook.interfaces
import urlparse
import z3c.table.column
import zope.app.publication.traversers
import zope.publisher.interfaces
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
    """Special link column which keeps the entity name in the url."""

    def getLinkURL(self, item):
        entities = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntities)
        url = zope.component.getMultiAdapter(
            (entities, self.request),
            zope.traversing.browser.interfaces.IAbsoluteURL)()
        url += "/" + self.context.__name__ + "/" + item.__name__
        if self.linkName:
            url += '/' + self.linkName
        return url

    def getLinkContent(self, item):
        return zope.i18n.translate(
            super(LinkColumn, self).getLinkContent(item), context=self.request)

    def renderCell(self, item):
        if icemac.addressbook.interfaces.IField.providedBy(item):
            return super(LinkColumn, self).renderCell(item)
        return ''


class List(icemac.addressbook.browser.table.PageletTable):
    """List fields of an entity."""

    sortOn = None # do not sort

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, z3c.table.column.I18nGetAttrColumn, 'title', weight=1,
                header=_(u'Field'), attrName='title'),
            z3c.table.column.addColumn(
                self, LinkColumn, 'delete', weight=190, header=_(u''),
                linkContent=_(u'Delete'), linkName='@@delete.html'),
            z3c.table.column.addColumn(
                self, LinkColumn, 'edit', weight=200, header=_(u''),
                linkContent=_(u'Edit')),
            ]

    @property
    def values(self):
        # zope.schema fields are no content classes, so they have no
        # permissions defined
        return [zope.security.proxy.getObject(field)
                for name, field in self.context.getRawFields()]


class AddForm(icemac.addressbook.browser.base.BaseAddForm):

    class_ = icemac.addressbook.entities.Field
    interface = icemac.addressbook.interfaces.IField
    next_url = 'parent'

    def add(self, obj):
        self._name = icemac.addressbook.entities.store_and_register_field(
            obj, zope.security.proxy.getObject(self.context))


class BaseForm(object):

    def redirect_to_next_url(self, *args):
        # redirect to the entity
        self.request.response.redirect(self.request.getURL(2))


class EditForm(BaseForm, icemac.addressbook.browser.base.GroupEditForm):

    interface = icemac.addressbook.interfaces.IField
    groups = (icemac.addressbook.browser.metadata.MetadataGroup,)


class DeleteForm(BaseForm, icemac.addressbook.browser.base.BaseDeleteForm):

    label = _(
        u'Caution: When you delete this field, possibly data will get lost. '
        u'Namely the data which was entered into this field when it was '
        u'displayed in a form of an object.')
    interface = icemac.addressbook.interfaces.IField
    field_names = ('type', 'title', 'notes')

    def _do_delete(self):
        # We need the name of the entity from the url here to
        # unregister the adapter.
        path = urlparse.urlsplit(self.request.getURL()).path
        entity_name = path.split('/')[-3]
        entity = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntity, name=entity_name)
        sm = zope.site.hooks.getSiteManager()
        sm.unregisterAdapter(
            provided=icemac.addressbook.interfaces.IField,
            required=(icemac.addressbook.interfaces.IEntity, entity.interface),
            name=self.context.__name__)
        return super(DeleteForm, self)._do_delete()

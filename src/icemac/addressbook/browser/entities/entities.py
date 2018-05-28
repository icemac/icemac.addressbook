# -*- coding: utf-8 -*-
from icemac.addressbook.i18n import _
import grokcore.component as grok
import icemac.addressbook.browser.base
import icemac.addressbook.browser.breadcrumb
import icemac.addressbook.browser.menus.menu
import icemac.addressbook.browser.table
import icemac.addressbook.interfaces
import six
import z3c.flashmessage.interfaces
import z3c.table.column
import zope.container.traversal
import zope.location
import zope.publisher.interfaces.http
import zope.security.proxy
import zope.traversing.browser.absoluteurl


class EntitiesBreadCrumb(
        icemac.addressbook.browser.breadcrumb.MasterdataChildBreadcrumb):
    """Breadcrumb for the entities."""

    grok.adapts(
        icemac.addressbook.interfaces.IEntities,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    title = _('Entities')


class UpLinkColumn(icemac.addressbook.browser.table.LinkColumn):
    """Column displaying an `up` link."""

    header = _('move-up-table-header', default='move')
    linkName = 'up.html'
    linkContent = _('move-up-table-cell', default='up')

    def renderCell(self, item):
        order = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntityOrder)
        if order.isFirst(item):
            return u''
        return super(UpLinkColumn, self).renderCell(item)


class DownLinkColumn(icemac.addressbook.browser.table.LinkColumn):
    """Column displaying an `down` link."""

    header = _('move-down-table-header', default='move')
    linkName = 'down.html'
    linkContent = _('move-down-table-cell', default='down')

    def renderCell(self, item):
        order = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntityOrder)
        if order.isLast(item):
            return u''
        return super(DownLinkColumn, self).renderCell(item)


class EditFieldsLinkColumn(icemac.addressbook.browser.table.LinkColumn):
    """LinkColumn only displaying a link for IMayHaveUserFields items."""

    linkContent = _(u'Edit fields')
    header = u''

    def renderCell(self, item):
        if icemac.addressbook.interfaces.IEditableEntity.providedBy(item):
            return super(EditFieldsLinkColumn, self).renderCell(item)
        return ''


class List(icemac.addressbook.browser.table.Table):
    """List existing entities."""

    title = icemac.addressbook.browser.breadcrumb.DO_NOT_SHOW
    sortOn = None  # do not sort rows

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, z3c.table.column.I18nGetAttrColumn, 'title', weight=10,
                header=_(u'Entity'), attrName='title'),
            z3c.table.column.addColumn(
                self, UpLinkColumn, 'up', weight=20),
            z3c.table.column.addColumn(
                self, DownLinkColumn, 'down', weight=30),
            z3c.table.column.addColumn(
                self, EditFieldsLinkColumn, 'fields', weight=100)]

    @property
    def values(self):
        # Need to remove security otherwise local administrators get
        # an unauthorized exception.
        for x in self.context.getEntities():
            yield zope.security.proxy.getObject(x)


@zope.component.adapter(
    icemac.addressbook.interfaces.IEntity,
    zope.publisher.interfaces.http.IHTTPRequest)
class EntityAbsoluteURL(zope.traversing.browser.absoluteurl.AbsoluteURL):
    """AbsoluteURL adapter for an entity."""

    def __str__(self):
        # parent is the entities utility and name is the class name
        parent = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntities)
        url = str(zope.component.getMultiAdapter(
            (parent, self.request),
            zope.traversing.browser.interfaces.IAbsoluteURL))
        url += '/' + self.context.class_name
        return url


@zope.component.adapter(
    icemac.addressbook.interfaces.IEntities,
    zope.publisher.interfaces.http.IHTTPRequest)
@zope.interface.implementer_only(zope.publisher.interfaces.IPublishTraverse)
class EntitiesTraverser(zope.container.traversal.ItemTraverser):
    """Make entities located and traverable."""

    def publishTraverse(self, request, name):
        entity = zope.component.queryUtility(
            icemac.addressbook.interfaces.IEntity, name=name)
        if entity is not None:
            return zope.location.LocationProxy(entity, self.context, name)
        return super(EntitiesTraverser, self).publishTraverse(request, name)


class MoveBase(icemac.addressbook.browser.base.BaseView):
    """Base class for movement views."""

    direction = None  # set on sub-class

    def __call__(self):
        order = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntityOrder)
        getattr(order, self.direction)(self.context)
        self.request.response.redirect(self.url(self.context.__parent__))
        message = _(six.text_type(self.message),
                    mapping=dict(entity=self.context.title))
        zope.component.getUtility(
            z3c.flashmessage.interfaces.IMessageSource).send(message)


class MoveUp(MoveBase):
    """Move entity up in entity order."""

    direction = 'up'
    message = _('Moved ${entity} up.')


class MoveDown(MoveBase):
    """Move entity down in entity order."""

    direction = 'down'
    message = _('Moved ${entity} down.')


entity_views = icemac.addressbook.browser.menus.menu.SelectMenuItemOn(
    icemac.addressbook.interfaces.IEntities,
    icemac.addressbook.interfaces.IEntity,
    icemac.addressbook.interfaces.IField)

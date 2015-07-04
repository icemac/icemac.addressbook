# -*- coding: utf-8 -*-
from icemac.addressbook.i18n import _
import icemac.addressbook.browser.metadata
import icemac.addressbook.entities
import icemac.addressbook.interfaces
import urlparse
import z3c.form.group
import z3c.formui.form
import zope.app.publication.traversers
import zope.publisher.interfaces
import zope.publisher.interfaces.http
import zope.security.proxy
import zope.traversing.browser


class FieldsTraverser(
        zope.app.publication.traversers.SimpleComponentTraverser):

    """Make fields traversable."""

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


def get_field_URL(entity, field, request, view=None):
    """Compute the URL to access a field."""
    entities = zope.component.getUtility(
        icemac.addressbook.interfaces.IEntities)
    url_parts = [zope.traversing.browser.absoluteURL(entities, request),
                 entity.__name__,
                 field.__name__]
    if view is not None:
        url_parts.append('@@%s' % view)
    return '/'.join(url_parts)


class MetadataForm(z3c.form.group.GroupForm, z3c.formui.form.Form):

    """Form to only render metadata."""

    id = 'standalone-metadata-form'
    groups = (icemac.addressbook.browser.metadata.MetadataGroup,)


class List(object):

    """List fields of an entity."""

    def _values(self):
        # zope.schema fields are no content classes, so they have no
        # permissions defined
        return [zope.security.proxy.getObject(field)
                for name, field in self.context.getRawFields()]

    def fields(self):
        for field in self._values():
            omit = False
            if icemac.addressbook.interfaces.IField.providedBy(field):
                url = get_field_URL(self.context, field, self.request)
                delete_url = get_field_URL(
                    self.context, field, self.request, 'delete.html')
            else:
                url = delete_url = None
                omit = field.queryTaggedValue('omit-from-field-list', False)
            if not omit:
                yield {'title': field.title,
                       'delete-link': delete_url,
                       'edit-link': url,
                       'id': field.__name__}

    def metadata(self):
        # Entities are not persisitent. Because the sort order of the fields
        # is shown in the list, we show the metadata of of this sort order:
        os = zope.component.getUtility(
            icemac.addressbook.interfaces.IOrderStorage)
        try:
            context = os.byNamespace(self.context.order_storage_namespace)
        except KeyError:
            # Sort order not yet changed, so we have no metadata:
            return ''
        form = MetadataForm(context, self.request)
        # We cannot use form() here as this renders the layout template,
        # too, which is not needed here:
        form.update()
        return form.render()


class SaveSortorder(icemac.addressbook.browser.base.BaseView):

    """Save the field sort order as defined by user."""

    def __call__(self, f):
        self.context.setFieldOrder(f)
        self.send_flash(_('Saved sortorder.'))
        self.request.response.redirect(self.url(self.context))


class AddForm(icemac.addressbook.browser.base.BaseAddForm):

    """Add a new user defined field to an entity."""

    label = _(u'Add new field')
    class_ = icemac.addressbook.entities.Field
    interface = icemac.addressbook.interfaces.IField
    next_url = 'parent'

    def add(self, obj):
        self._name = zope.security.proxy.getObject(self.context).addField(obj)


class BaseForm(object):

    """Mix-in class redirecting back to the entity."""

    def redirect_to_next_url(self, *args):
        # redirect to the entity
        self.request.response.redirect(self.request.getURL(2))


class EditForm(BaseForm, icemac.addressbook.browser.base.GroupEditForm):

    """Edit a user defined field on an entity."""

    label = _(u'Edit field')
    interface = icemac.addressbook.interfaces.IField
    groups = (icemac.addressbook.browser.metadata.MetadataGroup,)


class DeleteForm(BaseForm, icemac.addressbook.browser.base.BaseDeleteForm):

    """Delete a user defined field from an entity."""

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
        # XXX Without the following line removing the interface from the field
        #     (``field.interface = None`` in ``removeField``) fails with a
        #     ForbiddenAttribute error:
        field = zope.proxy.removeAllProxies(self.context)
        entity.removeField(field)
        # We have no need for a super call here as `removeField()` already
        # did the job.

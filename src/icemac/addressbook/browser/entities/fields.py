# -*- coding: utf-8 -*-
from icemac.addressbook.i18n import _
from icemac.addressbook.interfaces import IMayHaveCustomFieldLabels
from six.moves.urllib_parse import urlsplit
import grokcore.component as grok
import icemac.addressbook.browser.breadcrumb
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.metadata
import icemac.addressbook.entities
import icemac.addressbook.interfaces
import z3c.form.group
import z3c.form.interfaces
import z3c.form.widget
import z3c.formui.form
import zope.app.publication.traversers
import zope.component
import zope.interface
import zope.location
import zope.publisher.interfaces
import zope.publisher.interfaces.http
import zope.schema
import zope.schema.interfaces
import zope.security.proxy
import zope.traversing.browser


class FieldBreadCrumb(
        icemac.addressbook.browser.breadcrumb.Breadcrumb):
    """Breadcrumb for a user defined Field."""

    grok.adapts(
        icemac.addressbook.interfaces.IField,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    @property
    def parent(self):
        return icemac.addressbook.interfaces.IEntity(self.context)


class IProxiedField(zope.interface.Interface):
    """Wrapped zope.schema field used for renaming its title."""

    title = zope.schema.TextLine(
        title=_('title'),
        description=_(
            'Delete the value and submit the form to reset to the default'
            ' value.'))


@zope.interface.implementer(IProxiedField)
class ProxiedField(object):
    """Wrapper for a zope.schema field to allow access to the title attrib.

    This wrapper is located, it has:
    * __parent__ ... entity, the field belongs to
    * __name__ ... name of the field in the interface.
    """

    def __init__(self, field):
        pass

    @property
    def title(self):
        return self._field_labels.get_label(self._field)

    @title.setter
    def title(self, value):
        return self._field_labels.set_label(self._field, value)

    @property
    def _field_labels(self):
        address_book = icemac.addressbook.interfaces.IAddressBook(
            self.__parent__)
        return icemac.addressbook.interfaces.IFieldLabels(address_book)

    @property
    def _field(self):
        return self.__parent__.interface[self.__name__]


@zope.component.adapter(
    icemac.addressbook.interfaces.IEntity,
    zope.publisher.interfaces.http.IHTTPRequest)
@zope.interface.implementer_only(zope.publisher.interfaces.IPublishTraverse)
class FieldsTraverser(
        zope.app.publication.traversers.SimpleComponentTraverser):
    """Make fields traversable."""

    def publishTraverse(self, request, name):
        entities = zope.component.queryUtility(
            icemac.addressbook.interfaces.IEntities)
        try:
            return entities[name]
        except KeyError:
            try:
                field = self.context.interface[name]
            except KeyError:
                return super(FieldsTraverser, self).publishTraverse(
                    request, name)
            else:
                proxy = ProxiedField(field)
                zope.location.locate(proxy, self.context, name)
                return proxy


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


class List(icemac.addressbook.browser.base.FlashView):
    """List fields of an entity."""

    title = _('Edit fields')

    def _values(self):
        # zope.schema fields are no content classes, so they have no
        # permissions defined
        return [zope.security.proxy.getObject(field)
                for name, field in self.context.getRawFields()]

    def fields(self):
        have_custom_filed_labels = IMayHaveCustomFieldLabels.implementedBy(
            self.context.getClass())
        for field in self._values():
            omit = False
            if icemac.addressbook.interfaces.IField.providedBy(field):
                url = get_field_URL(self.context, field, self.request)
                delete_url = get_field_URL(
                    self.context, field, self.request, 'delete.html')
            else:
                if have_custom_filed_labels:
                    url = get_field_URL(self.context, field, self.request)
                else:
                    url = None
                delete_url = None
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

    title = _(u'Add new field')
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

    title = _(u'Edit field')
    interface = icemac.addressbook.interfaces.IField
    groups = (icemac.addressbook.browser.metadata.MetadataGroup,)


class DeleteForm(BaseForm, icemac.addressbook.browser.base.BaseDeleteForm):
    """Delete a user defined field from an entity."""

    title = _('Delete field')
    label = _(
        'Caution: When you delete this field, possibly data will get lost. '
        'Namely the data which was entered into this field when it was '
        'displayed in a form of an object.')
    interface = icemac.addressbook.interfaces.IField
    field_names = ('type', 'title', 'notes')

    def _do_delete(self):
        # We need the name of the entity from the url here to
        # unregister the adapter.
        path = urlsplit(self.request.getURL()).path
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
        return True


def get_field_label(self):
    """Get the label for a schema field which is possibly custom.

    self … ComputedWidgetAttribute instance with the attributes context and
           field.
    """
    address_book = icemac.addressbook.interfaces.IAddressBook(self.context)
    field_labels = icemac.addressbook.interfaces.IFieldLabels(address_book)
    return field_labels.get_label(self.field)


custom_field_label = z3c.form.widget.ComputedWidgetAttribute(
    get_field_label,
    context=IMayHaveCustomFieldLabels,
    field=zope.schema.interfaces.IField)


class RenameForm(BaseForm, icemac.addressbook.browser.base.BaseEditForm):
    """Rename the title of a pre-defined field on an entity."""

    title = _(u'Rename field')
    interface = IProxiedField

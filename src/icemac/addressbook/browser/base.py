# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.browser.interfaces
import icemac.addressbook.interfaces
import icemac.addressbook.utils
import transaction
import z3c.form.button
import z3c.form.field
import z3c.form.group
import z3c.formui.form
import zope.component
import zope.interface
import zope.security
import zope.security.interfaces
import zope.traversing.api
import zope.traversing.browser.interfaces
import zope.traversing.publicationtraverse


class display_title(object):

    zope.component.adapts(
        zope.interface.Interface,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)
    zope.interface.implements(icemac.addressbook.interfaces.ITitle)

    def __init__(self, context, request):
        self.context = context

    def __call__(self):
        return icemac.addressbook.interfaces.ITitle(self.context)


def create(form, class_, data):
    obj = icemac.addressbook.utils.create_obj(class_)
    z3c.formui.form.applyChanges(form, obj, data)
    return obj


def all_(*constraints):
    """All given button constraints must evaluate to true."""
    return lambda form: all(constraint(form) for constraint in constraints)


class BaseView(object):
    "Base for view classes."

    def url(self, obj):
        adapter = zope.component.getMultiAdapter(
            (obj, self.request),
            zope.traversing.browser.interfaces.IAbsoluteURL)
        return adapter()


class BaseForm(BaseView):
    """Base for all forms."""

    interface = None # interface for form

    @property
    def fields(self):
        fields = icemac.addressbook.interfaces.IEntity(self.interface)
        return z3c.form.field.Fields(*fields.getFieldValuesInOrder())


class BaseAddForm(BaseForm, z3c.formui.form.AddForm):
    """Simple base add form."""

    class_ = None # create object from this class
    next_url = None # target after creation, one of ('object', 'parent')


    def createAndAdd(self, data):
        # overwriting method as otherwise object created event would
        # get send twice
        obj = self.create(data)
        self.add(obj)
        return obj

    def create(self, data):
        return create(self, self.class_, data)

    def add(self, obj):
        try:
            self._name = icemac.addressbook.utils.add(self.context, obj)
        except zope.interface.Invalid, e:
            transaction.doom()
            raise z3c.form.interfaces.ActionExecutionError(e)

    @z3c.form.button.buttonAndHandler(_('Add'), name='add')
    def handleAdd(self, action):
        # because we define a new action we have to duplicate the
        # existing action because otherwise we'll lose it.
        super(BaseAddForm, self).handleAdd(self, action)

    @z3c.form.button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        self.next_url = 'parent'
        self._finishedAdd = True

    def nextURL(self):
        if self.next_url == 'object':
            context = self.context[self._name]
        elif self.next_url == 'parent':
            context = self.context
        else:
            raise ValueError("Don't know how to handle next_url %r.")
        return self.url(context)


class BaseEditForm(BaseForm, z3c.formui.form.EditForm):
    """Base Edit form."""

    next_url = None # target object after edit, one of ('object', 'parent')
    next_view = None # target view after edit (None for default view)

    def render(self):
        if self.request.response.getStatus() in (302, 303, 304):
            # redirecting
            return ''
        if self.status in (self.successMessage, self.noChangesMessage):
            self.redirect_to_next_url()
        else:
            return super(BaseEditForm, self).render()

    def redirect_to_next_url(self, next_url=None, next_view=None):
        if next_url is None:
            next_url = self.next_url
        if next_url == 'object':
            target = self.context
        elif next_url == 'parent':
            target = zope.traversing.api.getParent(self.context)
        else:
            raise ValueError('next_url %r unknown' % next_url)
        target_url = self.url(target)
        if next_view is None:
            next_view = self.next_view
        if next_view:
            target_url += '/%s' % next_view
        self.request.response.redirect(target_url)

    def applyChanges(self, data):
        try:
            super(BaseEditForm, self).applyChanges(data)
        except zope.interface.Invalid, e:
            transaction.doom()
            raise z3c.form.interfaces.ActionExecutionError(e)


class BaseEditFormWithCancel(BaseEditForm):
    "BaseEditForm with cancel button."

    @z3c.form.button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        # because we define a new action we have to duplicate the
        # existing action because otherwise we'll lose it.
        super(BaseEditFormWithCancel, self).handleApply(self, action)

    @z3c.form.button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        self.status = self.noChangesMessage


class GroupEditForm(z3c.form.group.GroupForm, BaseEditForm):
    "BaseEditForm as group form."


class BaseDeleteForm(BaseEditForm):
    "Display a deletion confirmation dialog."

    label = _(u'Do you really want to delete this entry?')
    requiredInfo = None # do never display requiredInfo
    interface = None
    field_names = () # tuple of field names for display; empty for all
    next_view_after_delete = None # when None, use same view as self.next_view

    mode = z3c.form.interfaces.DISPLAY_MODE
    next_url = 'object'

    @property
    def fields(self):
        fields = super(BaseDeleteForm, self).fields
        if self.field_names:
            fields = fields.select(*self.field_names)
        return fields

    @z3c.form.button.buttonAndHandler(_(u'No, cancel'), name='cancel')
    def handleCancel(self, action):
        self.status = self.noChangesMessage

    @z3c.form.button.buttonAndHandler(_(u'Yes, delete'), name='delete')
    def handleDelete(self, action):
        self.redirect_to_next_url('parent', self.next_view_after_delete)
        self._do_delete()

    def _do_delete(self):
        name = zope.traversing.api.getName(self.context)
        parent = zope.traversing.api.getParent(self.context)
        del parent[name]


class PrefixGroup(z3c.form.group.Group):
    """Group which sets a prefix."""

    prefix = None # to be set in subclass
    interface = None # to be set in subclass

    @property
    def fields(self):
        fields = icemac.addressbook.interfaces.IEntity(self.interface)
        return z3c.form.field.Fields(
            *fields.getFieldValuesInOrder(), **dict(prefix=self.prefix))


class CloneObject(BaseView):
    """View class to clone an object and store the clone into the parent.

    Redirects to the default view of the clone."""

    def __call__(self):
        # clone object
        unsecure_context = zope.security.proxy.getObject(self.context)
        copier = zope.copypastemove.interfaces.IObjectCopier(unsecure_context)
        parent = self.context.__parent__
        new_name = copier.copyTo(parent)
        # redirect to clone
        self.request.response.redirect(self.url(parent[new_name]))


def can_access(uri_part):
    """Create a button condition function to test whether the user can
    access the URL context/@@absolute_url/<uri_part>."""
    def can_access_form(form):
        traverser = zope.traversing.publicationtraverse.PublicationTraverser()
        try:
            view = traverser.traverseRelativeURL(
                form.request, form.context, uri_part)
        except (zope.security.interfaces.Unauthorized,
                zope.security.interfaces.Forbidden,
                LookupError):
            return False
        else:
            # we're assuming that view pages are callable
            # this is a pretty sound assumption
            if not zope.security.canAccess(view, '__call__'):
                return False
        return True
    return can_access_form


# -*- coding: latin-1 -*-
# Copyright (c) 2008-2013 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import _
import classproperty
import gocept.reference.interfaces
import grokcore.component
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.resource
import icemac.addressbook.interfaces
import icemac.addressbook.utils
import transaction
import z3c.flashmessage.interfaces
import z3c.form.button
import z3c.form.field
import z3c.form.group
import z3c.formui.form
import zope.component
import zope.interface
import zope.security
import zope.security.interfaces
import zope.security.proxy
import zope.session.interfaces
import zope.site.hooks
import zope.traversing.api
import zope.traversing.browser
import zope.traversing.publicationtraverse


class display_title(object):
    """ITitle adapter which can be used in PageTemplate using
    ``obj/@@display_title``.

    """
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


def get_needed_resources(self):
    """Get the needed resources for self."""
    if self.need:
        getattr(icemac.addressbook.browser.resource, self.need).need()


class FlashView(object):
    """Base class to send flash messages."""

    def send_flash(self, message):
        zope.component.getUtility(
            z3c.flashmessage.interfaces.IMessageSource).send(message)


class BaseView(FlashView):
    "Base for view classes."

    need = None  # name of a resource from icemac.addressbook.browser.resource

    def update(self):
        get_needed_resources(self)
        super(BaseView, self).update()

    def url(self, obj, view_name=None):
        url = zope.traversing.browser.absoluteURL(obj, self.request)
        if view_name:
            url += '/' + view_name
        return url


class BaseForm(BaseView):
    """Base for all forms."""

    interface = None  # interface for form
    need = 'form_css'

    # privat
    _status = ''
    _fields = None

    @property
    def fields(self):
        if self._fields is not None:
            return self._fields
        if self.interface is None:
            field_values = ()
        else:
            fields = icemac.addressbook.interfaces.IEntity(self.interface)
            field_values = fields.getFieldValues()
        self._fields = z3c.form.field.Fields(*field_values)
        return self._fields

    @fields.setter
    def fields(self, fields):
        if self._fields is not None:
            raise ValueError('fields is already set')
        self._fields = fields

    class status(classproperty.classproperty):
        def __get__(self):
            return self._status

        def __set__(self, message):
            if message != z3c.form.form.Form.formErrorsMessage:
                # Non-error messages must be handled by z3c.flashmessage,
                # too, as they must be displayed on the next page after the
                # redirect. But we need them to determine whether a redirect
                # is necessary, too.
                self.send_flash(message)
            self._status = message


class BaseAddForm(BaseForm, z3c.formui.form.AddForm):
    """Simple base add form."""

    class_ = None  # create object from this class
    next_url = None  # target after creation, one of ('object', 'parent')
    next_view = None  # target view after creation, None --> default view

    def createAndAdd(self, data):
        # overwriting method as otherwise object created event would
        # get send twice
        self.obj = self.create(data)
        self.add(self.obj)
        return self.obj

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
        if self._finishedAdd:
            self.status = _(
                '"${title}" added.',
                mapping=dict(title=icemac.addressbook.interfaces.ITitle(
                    self.obj)))

    @z3c.form.button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        self.next_url = 'parent'
        self._finishedAdd = True
        self.status = _('Addition canceled.')

    def nextURL(self):
        if self.next_url == 'object':
            context = self.context[self._name]
        elif self.next_url == 'parent':
            context = self.context
        else:
            raise ValueError("Don't know how to handle next_url %r.")
        return self.url(context, self.next_view)


def update_with_redirect(class_, self):
    """Call update of super class and redirect when necessary."""
    get_needed_resources(self)
    # Caution: we need the class_ parameter as we get infinite recursion if
    # using self.__class__ in the super call.
    super(class_, self).update()
    if self.request.response.getStatus() in (302, 303, 304):
        # already redirecting
        return
    if self.status in (self.successMessage, self.noChangesMessage):
        self.redirect_to_next_url()


class _AbstractEditForm(BaseForm, z3c.formui.form.EditForm):
    """Abstract base class for edit forms.

    CAUTION: Not to be used as direct base class of forms, use one of its
             child classes!

    """
    next_url = None  # target object after edit, one of ('object', 'parent')
    next_view = None  # target view after edit (None for default view)
    id = 'edit-form'

    def update(self):
        update_with_redirect(_AbstractEditForm, self)

    def redirect_to_next_url(self, next_url=None, next_view=None):
        if next_url is None:
            next_url = self.next_url
        if next_url == 'object':
            target = self.context
        elif next_url == 'parent':
            target = zope.traversing.api.getParent(self.context)
        elif next_url == 'site':
            target = zope.site.hooks.getSite()
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
            return super(_AbstractEditForm, self).applyChanges(data)
        except zope.interface.Invalid, e:
            transaction.doom()
            raise z3c.form.interfaces.ActionExecutionError(e)


class BaseEditForm(_AbstractEditForm):
    """Base edit form.

    It has a cancel button registered on it.
    """


class EditActions(z3c.form.button.ButtonActions,
                  grokcore.component.MultiAdapter):
    """Custom edit actions to add a cancel button on each edit form."""

    grokcore.component.adapts(BaseEditForm,
                              zope.interface.Interface,
                              zope.interface.Interface)

    def update(self):
        self.form.buttons = z3c.form.button.Buttons(
            self.form.buttons,
            z3c.form.button.Button('cancel', _(u'Cancel')))
        super(EditActions, self).update()


class EditActionHandler(z3c.form.button.ButtonActionHandler,
                        grokcore.component.MultiAdapter):
    """Edit action handler which is able to handle the cancel action."""

    grokcore.component.adapts(BaseEditForm,
                              zope.interface.Interface,
                              zope.interface.Interface,
                              z3c.form.button.ButtonAction)

    def __call__(self):
        if self.action.name == 'form.buttons.cancel':
            self.form.status = self.form.noChangesMessage
            return
        super(EditActionHandler, self).__call__()


class GroupEditForm(z3c.form.group.GroupForm, BaseEditForm):
    """EditForm (with cancel) as group form."""

    # This is needed here as GroupForm does not do a super-call.
    def update(self):
        update_with_redirect(GroupEditForm, self)


class BaseDeleteForm(_AbstractEditForm):
    "Display a deletion confirmation dialog."

    label = _(u'Do you really want to delete this entry?')
    requiredInfo = None  # do never display requiredInfo
    interface = None
    field_names = ()  # tuple of field names for display; empty for all
    next_view_after_delete = None  # None --> default view

    need = 'no_max_content_css'
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
        self.redirect_to_next_url(self.next_url)
        self.status = _('Deletion canceled.')

    @z3c.form.button.buttonAndHandler(_(u'Yes, delete'), name='delete')
    def handleDelete(self, action):
        self._handle_delete()

    def _handle_delete(self):
        self.redirect_to_next_url('parent', self.next_view_after_delete)
        self.status = _(
            '"${title}" deleted.',
            mapping=dict(
                title=icemac.addressbook.interfaces.ITitle(self.context)))
        self._do_delete()

    def _do_delete(self):
        name = zope.traversing.api.getName(self.context)
        parent = zope.traversing.api.getParent(self.context)
        del parent[name]


def delete_persons(address_book, ids):
    """Delete persons specified by their ID, but not users."""
    deleted = 0
    for name in list(ids):  # this list() call is needed as we might delete
                            # from the source of the ids
        ref_target = gocept.reference.interfaces.IReferenceTarget(
            zope.security.proxy.getObject(address_book[name]))
        if ref_target.is_referenced(recursive=False):
            # Persons which are referenced by a user can't be
            # deleted using this function. We check this here to
            # avoid getting an error.
            continue
        del address_book[name]
        deleted += 1
    return deleted


class PrefixGroup(z3c.form.group.Group):
    """Group which sets a prefix."""

    prefix = None  # to be set in subclass
    interface = None  # to be set in subclass

    @property
    def fields(self):
        fields = icemac.addressbook.interfaces.IEntity(self.interface)
        return z3c.form.field.Fields(
            *fields.getFieldValues(), **dict(prefix=self.prefix))


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
        zope.component.getUtility(
            z3c.flashmessage.interfaces.IMessageSource).send(
            _('"${object}" cloned.', mapping=dict(
                object=icemac.addressbook.interfaces.ITitle(self.context))))


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


def get_session(request):
    """Get the browser session of the current user."""
    return zope.session.interfaces.ISession(request)[
        icemac.addressbook.interfaces.PACKAGE_ID]

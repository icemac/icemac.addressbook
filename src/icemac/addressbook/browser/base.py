# -*- coding: latin-1 -*-
from icemac.addressbook.i18n import _
import gocept.reference.interfaces
import grokcore.component
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.resource
import icemac.addressbook.interfaces
import icemac.addressbook.utils
import transaction
import urllib
import z3c.flashmessage.interfaces
import z3c.form.button
import z3c.form.field
import z3c.form.group
import z3c.form.util
import z3c.formui.form
import zope.component
import zope.component.hooks
import zope.interface
import zope.security
import zope.security.interfaces
import zope.security.proxy
import zope.session.interfaces
import zope.traversing.api
import zope.traversing.browser
import zope.traversing.publicationtraverse


def create(form, class_, data):
    """Create an object from a class and assign values."""
    obj = icemac.addressbook.utils.create_obj(class_)
    z3c.formui.form.applyChanges(form, obj, data)
    return obj


def all_(*constraints):
    """All given button constraints must evaluate to true."""
    return lambda form: all(constraint(form) for constraint in constraints)


class FlashView(object):
    """Base class to send flash messages."""

    title = None  # used by the breadrumbs

    def send_flash(self, message):
        zope.component.getUtility(
            z3c.flashmessage.interfaces.IMessageSource).send(message)


class BaseView(FlashView):
    """Base for view classes."""

    __PACKAGE_ID__ = icemac.addressbook.interfaces.PACKAGE_ID

    def url(self, obj, view_name=None, **kw):
        url_parts = [zope.traversing.browser.absoluteURL(obj, self.request)]
        if view_name:
            url_parts.append('/')
            if not view_name.startswith('++'):
                url_parts.append('@@')
            url_parts.append(view_name)
        if kw:
            url_parts.extend(['?', urllib.urlencode(kw, doseq=True)])
        return ''.join(url_parts)

    @property
    def session(self):
        return get_session(self.request, name=self.__PACKAGE_ID__)


class BaseForm(BaseView):
    """Base for all forms."""

    interface = None  # interface for form

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

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, message):
        if message != z3c.form.form.Form.formErrorsMessage:
            # Non-error messages must be handled by z3c.flashmessage, too, as
            # they must be displayed on the next page after the redirect. But
            # we need them to determine whether a redirect is necessary, too.
            self.send_flash(message)
        self._status = message


class BaseAddForm(BaseForm, z3c.formui.form.AddForm):
    """Simple base add form."""

    class_ = None  # create object from this class
    next_url = None  # target after creation, one of ('object', 'parent')
    next_view = None  # target view after creation, None --> default view
    _next_url_map = {
        'object': lambda self: self.context[self._name],
        'parent': lambda self: self.context
    }

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
        except zope.interface.Invalid as e:
            transaction.doom()
            raise z3c.form.interfaces.ActionExecutionError(e)

    @z3c.form.button.buttonAndHandler(_('Add'), name='add')
    def handleAdd(self, action):
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
        return self.url(self._next_url_map[self.next_url](self),
                        self.next_view)


def update_with_redirect(class_, self):
    """Call update of super class and redirect when necessary."""
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
    _next_url_map = {
        'object': lambda self: self.context,
        'parent': lambda self: zope.traversing.api.getParent(self.context),
        'site': lambda self: zope.component.hooks.getSite()
    }

    def update(self):
        update_with_redirect(_AbstractEditForm, self)

    def redirect_to_next_url(self, next_url=None, next_view=None):
        target = self._next_url_map[
            next_url if next_url else self.next_url](self)

        if next_view is None:
            next_view = self.next_view
        self.request.response.redirect(self.url(target, next_view))

    def applyChanges(self, data):
        try:
            return super(_AbstractEditForm, self).applyChanges(data)
        except zope.interface.Invalid as e:
            transaction.doom()
            raise z3c.form.interfaces.ActionExecutionError(e)


class BaseEditForm(_AbstractEditForm):
    """Base edit form.

    It has a cancel button registered on it and `Apply` is called `Save`.
    """

    @z3c.form.button.buttonAndHandler(_('Save'), name='apply')
    def handleApply(self, action):
        return super(_AbstractEditForm, self).handleApply(self, action)


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


class _BaseConfirmForm(_AbstractEditForm):
    """Display a confirmation dialog before the action.

    Subclasses have to implement the `yes` action.
    """

    label = NotImplemented
    interface = None
    field_names = ()  # tuple of field names for display; empty for all
    cancel_status_message = NotImplemented

    requiredInfo = None  # do never display requiredInfo
    mode = z3c.form.interfaces.DISPLAY_MODE
    next_url_after_cancel = 'object'

    def update(self):
        icemac.addressbook.browser.resource.no_max_content_css.need()
        super(_BaseConfirmForm, self).update()

    @property
    def fields(self):
        fields = super(_BaseConfirmForm, self).fields
        if self.field_names:
            fields = fields.select(*self.field_names)
        return fields

    @z3c.form.button.buttonAndHandler(_(u'No, cancel'), name='cancel')
    def handleCancel(self, action):
        self.redirect_to_next_url(self.next_url_after_cancel)
        self.status = self.cancel_status_message


class BaseDeleteForm(_BaseConfirmForm):
    """Display a deletion confirmation dialog."""

    label = _(u'Do you really want to delete this entry?')
    next_view_after_delete = None  # None --> default view
    next_url_after_delete = 'parent'
    cancel_status_message = _('Deletion canceled.')
    z3c.form.form.extends(_BaseConfirmForm, ignoreFields=True)

    @z3c.form.button.buttonAndHandler(_(u'Yes, delete'), name='action')
    def handleAction(self, action):
        self._handle_action()

    def _handle_action(self):
        self.redirect_to_next_url(self.next_url_after_delete,
                                  self.next_view_after_delete)
        if self._do_delete():
            self._set_status()

    def _set_status(self):
        self.status = _('"${title}" deleted.',
                        mapping={'title': self.status_title})

    def _do_delete(self):
        """Execute the deletion.

        Returns `True` on success.
        Subclasses may also handle failure. They have to return `False` and
        set the status message on their own.
        """
        icemac.addressbook.utils.delete(self.context)
        return True

    @property
    def status_title(self):
        return icemac.addressbook.interfaces.ITitle(self.getContent())


def delete_persons(address_book, ids):
    """Delete persons specified by their ID, but not users."""
    deleted = 0
    # The following list() call is needed as we might delete from the source of
    # the ids:
    for name in list(ids):
        ref_target = gocept.reference.interfaces.IReferenceTarget(
            zope.security.proxy.getObject(address_book[name]))
        if ref_target.is_referenced(recursive=False):
            # Persons which are referenced can't be deleted using this
            # function. We check this here to avoid getting an error.
            continue
        del address_book[name]
        deleted += 1
    return deleted


class PrefixGroup(z3c.form.group.Group):
    """Group which sets a prefix."""

    prefix = None  # to be set in subclass
    interface = None  # to be set in subclass
    # mapping between field name and  (mode, widgetFactory):
    widget_factories = {}

    @property
    def fields(self):
        fields = icemac.addressbook.interfaces.IEntity(self.interface)
        form_fields = z3c.form.field.Fields(
            *fields.getFieldValues(), **dict(prefix=self.prefix))
        for field_name, (mode, widgetFactory) in self.widget_factories.items():
            field_with_prefix = "".join(
                [z3c.form.util.expandPrefix(self.prefix), field_name])
            form_fields.get(field_with_prefix).widgetFactory[
                mode] = widgetFactory
        return form_fields


class BaseCloneForm(_BaseConfirmForm):
    """Display a cloning confirmation dialog."""

    label = _(u'Do you really want to clone this entry?')
    cancel_status_message = _('Cloning canceled.')
    z3c.form.form.extends(_BaseConfirmForm, ignoreFields=True)

    @z3c.form.button.buttonAndHandler(_(u'Yes, clone'), name='action')
    def handleAction(self, action):
        self._handle_action()

    def _handle_action(self):
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


def can_access_uri_part(context, request, uri_part):
    """Tell if current user can to access a URI part relative to context."""
    assert uri_part is not None
    traverser = zope.traversing.publicationtraverse.PublicationTraverser()
    try:
        view = traverser.traverseRelativeURL(request, context, uri_part)
    except (zope.security.interfaces.Unauthorized,
            zope.security.interfaces.Forbidden,
            LookupError):
        return False
    # We're assuming that view pages are callable this is a pretty sound
    # assumption:
    return zope.security.canAccess(view, '__call__')


def can_access(uri_part):
    """Button condition function to if access is allowed.

    Returns a function which tests whether the user can access the URL
    ``context/@@absolute_url/<uri_part>``.
    """
    def can_access_form(form):
        return can_access_uri_part(form.context, form.request, uri_part)
    return can_access_form


def tab_selected(tab):
    """Condition checker factory to test whether `tab` is selected."""
    def tab_selected(form):
        address_book = icemac.addressbook.interfaces.IAddressBook(None)
        return tab not in address_book.deselected_tabs
    return tab_selected


def get_session(request, name=icemac.addressbook.interfaces.PACKAGE_ID):
    """Get the browser session of the current user."""
    return zope.session.interfaces.ISession(request)[name]

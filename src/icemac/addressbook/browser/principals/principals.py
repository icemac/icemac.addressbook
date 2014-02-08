# -*- coding: utf-8 -*-
# Copyright (c) 2009-2014 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.browser.base
import icemac.addressbook.browser.metadata
import icemac.addressbook.browser.table
import icemac.addressbook.interfaces
import icemac.addressbook.principals.interfaces
import icemac.addressbook.principals.principals
import transaction
import z3c.form.button
import z3c.form.field
import z3c.form.validator
import z3c.form.widget
import zope.interface
import zope.schema
import zope.schema.interfaces
import zope.security


class Overview(icemac.addressbook.browser.table.PageletTable):

    no_rows_message = _(
        u'No users defined yet or you are not allowed to access any.')

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, icemac.addressbook.browser.table.TitleLinkColumn,
                'user', weight=1),
            z3c.table.column.addColumn(
                self, z3c.table.column.GetAttrColumn, 'login', weight=2,
                header=_(u'login name'), attrName='login'),
            z3c.table.column.addColumn(
                self, icemac.addressbook.browser.table.TruncatedContentColumn,
                'notes', weight=3,
                header=_(u'notes'), attrName='description', length=50),
            ]

    @property
    def values(self):
        for principal in self.context.values():
            if zope.security.canAccess(principal, 'login'):
                yield principal


class PersonFieldDataManager(z3c.form.datamanager.AttributeField):
    """Person is a readonly field which should be written once."""

    zope.component.adapts(
        icemac.addressbook.principals.interfaces.IPrincipal,
        zope.schema.interfaces.IChoice)

    def set(self, value):
        if self.context.person is not None:
            # was already set --> get error message from parent class
            super(PersonFieldDataManager, self).set(value)
        self.context.person = value


class AddForm(icemac.addressbook.browser.base.BaseAddForm):

    label = _(u'Add new user')
    class_ = icemac.addressbook.principals.principals.Principal
    interface = icemac.addressbook.principals.interfaces.IPrincipal
    next_url = 'parent'

    @property
    def fields(self):
        return (
            z3c.form.field.Fields(
                icemac.addressbook.principals.interfaces.IPrincipal).select(
                'person')
            +
            z3c.form.field.Fields(
                icemac.addressbook.principals.interfaces.IPasswordFields)
            +
            z3c.form.field.Fields(
                icemac.addressbook.principals.interfaces.IRoles)
            +
            z3c.form.field.Fields(
                *icemac.addressbook.interfaces.IEntity(
                    self.interface).getFieldValues()).omit(
                'login', 'person')
            )

    def add(self, obj):
        try:
            return super(AddForm, self).add(obj)
        except zope.container.interfaces.DuplicateIDError, e:
            transaction.doom()
            raise z3c.form.interfaces.ActionExecutionError(
                zope.interface.Invalid(_(e.args[0])))

# in the Add form the password fields are required ...
password_required = z3c.form.widget.StaticWidgetAttribute(
    True, context=None, request=None, view=AddForm, field=zope.schema.Password,
    widget=None)

# ... but not in all other forms
password_not_required = z3c.form.widget.StaticWidgetAttribute(
    False, context=icemac.addressbook.principals.interfaces.IPrincipal,
    request=None, view=None, field=zope.schema.Password, widget=None)


class EditForm(icemac.addressbook.browser.base.GroupEditForm):

    label = _(u'Edit user')
    groups = (icemac.addressbook.browser.metadata.MetadataGroup,)
    interface = icemac.addressbook.principals.interfaces.IPrincipal
    next_url = 'parent'

    @property
    def fields(self):
        return (
            z3c.form.field.Fields(
                icemac.addressbook.principals.interfaces.IPrincipal).select(
                'person', 'login')
            +
            z3c.form.field.Fields(
                icemac.addressbook.principals.interfaces.IPasswordFields)
            +
            z3c.form.field.Fields(
                icemac.addressbook.principals.interfaces.IRoles)
            +
            z3c.form.field.Fields(
                *icemac.addressbook.interfaces.IEntity(
                    self.interface).getFieldValues()).omit(
                'person', 'login')
            )

    @z3c.form.button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        # because we define a new action we have to duplicate the
        # existing action because otherwise we'll loose it.
        super(EditForm, self).handleApply(self, action)

    @z3c.form.button.buttonAndHandler(
        _(u'Delete user'), name='delete_user',
        condition=icemac.addressbook.browser.base.can_access(
            '@@delete_user.html'))
    def handleDeleteUser(self, action):
        self.redirect_to_next_url('object', '@@delete_user.html')

    def applyChanges(self, data):
        current_principal_id = (
            self.request.interaction.participations[0].principal.id)
        current_login_name = None
        auth = zope.component.getUtility(
            zope.authentication.interfaces.IAuthentication)
        for key, plugin in auth.getAuthenticatorPlugins():
            principal_info = plugin.principalInfo(current_principal_id)
            if principal_info is not None:
                current_login_name = principal_info.login
                break

        old_login_name = self.context.login
        editing_own_data = (old_login_name == current_login_name)
        try:
            changes = super(EditForm, self).applyChanges(data)
        except ValueError, e:
            transaction.doom()
            raise z3c.form.interfaces.ActionExecutionError(
                zope.interface.Invalid(_(e.args[0])))

        if not editing_own_data:
            # User is not editing his own data principal's data:
            return changes

        changed_field_names = []
        changed_field_names.extend(
            changes.get(
                icemac.addressbook.principals.interfaces.IPrincipal, []))
        changed_field_names.extend(
            changes.get(
                icemac.addressbook.principals.interfaces.IPasswordFields, []))
        if 'login' in changed_field_names:
            self.send_flash(_('You changed the login name, please re-login.'))
        if ('password' in changed_field_names and
            'password_repetition' in changed_field_names and
            data['password']):
            self.send_flash(_('You changed the password, please re-login.'))
        return changes


class EditForm_password_Validator(z3c.form.validator.SimpleFieldValidator):
    """Validator for data field in add form."""

    zope.component.adapts(
        icemac.addressbook.principals.interfaces.IPrincipal, None, EditForm,
        zope.schema.Password, None)

    def validate(self, value):
        if not value:
            # use a dummy value for validation, so passwords needn't
            # be entered everytime the edit form is saved
            value = u'asdfasdf'
        return super(EditForm_password_Validator, self).validate(value)


class DeleteUserForm(icemac.addressbook.browser.base.BaseDeleteForm):
    label = _(u'Do you really want to delete this user?')
    interface = icemac.addressbook.principals.interfaces.IPrincipal
    field_names = ('person', 'login')

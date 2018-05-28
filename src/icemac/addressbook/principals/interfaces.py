# -*- coding: utf-8 -*-
from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.principals.sources
import zope.interface
import zope.schema


class IPasswordFields(zope.interface.Interface):
    """Required password fields to enter and check password."""

    password = zope.schema.Password(
        title=_(u'password'), min_length=8,
        description=_(u'The password for the user.'))

    password_repetition = zope.schema.Password(
        title=_(u'password repetition'), min_length=8,
        description=_(u'Please repeat the password.'))

    @zope.interface.invariant
    def password_eq_repetition(obj):
        if obj.password != obj.password_repetition:
            raise zope.interface.Invalid(
                _(u'Entry in password field was not equal to entry in '
                  u'password repetition field.'))


class IPrincipal(zope.interface.Interface):
    """Derived from ...

    ... zope.pluggableauth.plugins.principalfolder.IInternalPrincipal.
    """

    last_login = zope.interface.Attribute('Datetime of last login or `None`.')

    person = zope.schema.Choice(
        title=_(u'person'), readonly=True,
        source=icemac.addressbook.principals.sources.persons)

    login = zope.schema.TextLine(
        title=_(u'login name'),
        description=_(u'The Login/Username of the user. '
                      u'This value can change.'))

    description = zope.schema.Text(
        title=_('notes'),
        description=_('Provides notes for the user.'),
        required=False, missing_value='', default=u'')


class IRoles(zope.interface.Interface):
    """Roles"""

    roles = zope.schema.Tuple(
        title=_(u'roles'), required=False,
        value_type=zope.schema.Choice(
            source=icemac.addressbook.principals.sources.role_source))


class IRoot(zope.interface.Interface):
    """Root object on which global roles are stored.

    You have to provide an adapter from the root object to this interface.
    """


class IVisitorRole(zope.interface.Interface):
    """Role which is set on a user who is only allowed to read."""


class IEditorRole(zope.interface.Interface):
    """Role which is set on a user who is only allowed to read and write."""

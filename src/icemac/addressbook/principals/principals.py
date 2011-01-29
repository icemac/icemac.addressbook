# -*- coding: utf-8 -*-
# Copyright (c) 2009-2011 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import classproperty
import gocept.reference
import icemac.addressbook.interfaces
import icemac.addressbook.principals.interfaces
import zope.annotation.interfaces
import zope.pluggableauth.plugins.principalfolder
import zope.container.interfaces
import zope.interface
import zope.lifecycleevent
import zope.securitypolicy.interfaces


PASSWORD_MANAGER_NAME = 'SSHA'
EDITOR_VISITOR_PERMS = ('icemac.addressbook.EditPrincipalPassword',
                        'icemac.addressbook.ViewPrincipal',)
ONLY_EDITOR_PERMS = ('icemac.addressbook.EditPrincipal', )


class Principal(zope.pluggableauth.plugins.principalfolder.InternalPrincipal):
    """Principal where the password manager cannot be specified."""

    zope.interface.implements(
        icemac.addressbook.principals.interfaces.IPrincipal,
        icemac.addressbook.principals.interfaces.IPasswordFields,
        icemac.addressbook.principals.interfaces.IRoles,
        zope.annotation.interfaces.IAttributeAnnotatable)

    _person = gocept.reference.Reference('_person', ensure_integrity=True)
    _login = None
    _password = None
    description = None
    _roles = ()

    def __init__(self):
        self._passwordManagerName = PASSWORD_MANAGER_NAME

    @property
    def title(self):
        # needed by principal folder
        return icemac.addressbook.interfaces.ITitle(self.person)

    class person(classproperty.classproperty):
        def __get__(self):
            return self._person

        def __set__(self, person):
            if self._person is not None:
                # it's not possible to change the person
                return
            self._person = person
            self.login = person.default_email_address.email

    class password(classproperty.classproperty):
        def __get__(self):
            return self._password

        def __set__(self, password):
            if password is not None:
                zope.pluggableauth.plugins.principalfolder.InternalPrincipal.\
                    setPassword(self, password)

    class password_repetition(classproperty.classproperty):
        def __get__(self):
            pass  # password_repetition is not stored

        def __set__(self, password):
            pass  # password_repetition is not stored

    class roles(classproperty.classproperty):
        def __get__(self):
            return self._roles

        def __set__(self, roles):
            old_roles = self._roles
            self._roles = roles
            addressbook = icemac.addressbook.principals.interfaces.IRoot(self)
            # Update role map on addressbook
            role_manager = (
                zope.securitypolicy.interfaces.IPrincipalRoleManager(
                    addressbook))
            for role in old_roles:
                role_manager.unsetRoleForPrincipal(role, self.__name__)
            for role in roles:
                role_manager.assignRoleToPrincipal(role, self.__name__)

            # Update permission map on user
            permission_manager = (
                zope.securitypolicy.interfaces.IPrincipalPermissionManager(
                    self))

            for permission in EDITOR_VISITOR_PERMS + ONLY_EDITOR_PERMS:
                permission_manager.unsetPermissionForPrincipal(
                    permission, self.__name__)
            if ('icemac.addressbook.global.Editor' in roles or
                'icemac.addressbook.global.Visitor' in roles):
                for permission in EDITOR_VISITOR_PERMS:
                    permission_manager.grantPermissionToPrincipal(
                        permission, self.__name__)
            if 'icemac.addressbook.global.Editor' in roles:
                for permission in ONLY_EDITOR_PERMS:
                    permission_manager.grantPermissionToPrincipal(
                        permission, self.__name__)


@zope.component.adapter(
    icemac.addressbook.principals.interfaces.IPrincipal,
    zope.lifecycleevent.IObjectCreatedEvent)
def created(principal, event):
    """Create initial infrastructure or update existing infrastructure to
    current requirements (using generation)."""
    # set default values for references as z3c.form accesses the
    # attributes before a value is assigned and gets an AttributeError
    # otherwise
    if not hasattr(principal, '_person'):
        principal._person = None


@zope.component.adapter(
    icemac.addressbook.principals.interfaces.IPrincipal,
    zope.container.interfaces.IObjectAddedEvent)
def added(principal, event):
    # roles need principal.__name__ so we set them again when the
    # principal has been added
    principal.roles = principal._roles


@zope.component.adapter(icemac.addressbook.principals.interfaces.IPrincipal)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def title(principal):
    if getattr(principal, 'person', None) is not None:
        return icemac.addressbook.interfaces.ITitle(principal.person)
    # safty belt:
    return _(u'<no person>')

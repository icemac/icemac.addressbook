# -*- coding: utf-8 -*-
import icemac.addressbook.interfaces
import zc.sourcefactory.basic
import zc.sourcefactory.contextual
import zope.component
import zope.security.proxy
import zope.securitypolicy.interfaces


class RoleSource(zc.sourcefactory.basic.BasicSourceFactory):
    """A source for all global roles."""

    def getValues(self):
        roles = zope.component.getAllUtilitiesRegisteredFor(
            zope.securitypolicy.interfaces.IRole)
        names = [r.id
                 for r in roles
                 if (r.id.startswith('icemac.addressbook.global.') or
                     r.id.startswith('icemac.ab.'))]
        return sorted(names)

    def getTitle(self, value):
        role = zope.component.getUtility(
            zope.securitypolicy.interfaces.IRole, name=value)
        return role.title


role_source = RoleSource()


class Persons(zc.sourcefactory.contextual.BasicContextualSourceFactory):
    """Persons in addressbook."""

    def getValues(self, context):
        root = icemac.addressbook.principals.interfaces.IRoot(context)
        insecured_context = zope.security.proxy.removeSecurityProxy(context)
        # When editing a user we need this users person in list, as
        # the person on user is not changeable we need only to return
        # this person.
        if isinstance(insecured_context,  # XXX Use IPrincipal.providedBy?
                      icemac.addressbook.principals.principals.Principal):
            values = [context.person]
        else:
            values = []
            persons_of_existing_pricipals = frozenset(
                [principal.person for principal in context.values()])

            for person in root.values():
                if not getattr(person.default_email_address, 'email', None):
                    # Show only persons which have an e-mail address:
                    continue
                if person in persons_of_existing_pricipals:
                    # Show only persons which are not yet users:
                    continue
                values.append(person)
        return values

    def getTitle(self, context, value):
        return icemac.addressbook.interfaces.ITitle(value)


persons = Persons()

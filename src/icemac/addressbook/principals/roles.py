import icemac.addressbook.principals.interfaces
import zope.component


def editor_role(ignored):
    return 'icemac.addressbook.global.Editor'


def archivist_role(ignored):
    """Archivist role which has the same weighting as the Editor role."""
    return 'icemac.addressbook.global.Archivist'


def visitor_role(ignored):
    return 'icemac.addressbook.global.Visitor'


def _has_role(roles, role_interface):
    """Tell whether an a role specified by `role_interface` is in `roles`."""
    possible_roles = set(zope.component.subscribers((None,), role_interface))
    return not possible_roles.isdisjoint(set(roles))


def has_editor_role(roles):
    """Tell whether an editor role is in `roles`."""
    return _has_role(
        roles, icemac.addressbook.principals.interfaces.IEditorRole)


def has_visitor_role(roles):
    """Tell whether a visitor role is in `roles`."""
    return _has_role(
        roles, icemac.addressbook.principals.interfaces.IVisitorRole)

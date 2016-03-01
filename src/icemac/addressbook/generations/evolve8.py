# -*- coding: latin-1 -*-
import icemac.addressbook.generations.utils
import icemac.addressbook.utils
import zope.annotation.interfaces
import zope.authentication.interfaces
import zope.container.interfaces
import zope.dublincore.interfaces


generation = 8
MAX_DEPTH = 10


@icemac.addressbook.utils.set_site
def principal_id_to_title(id, context):
    """Convert a principal id into its title."""
    auth = zope.component.getUtility(
        zope.authentication.interfaces.IAuthentication)
    try:
        principal = auth.getPrincipal(id)
    except zope.authentication.interfaces.PrincipalLookupError:
        return id
    else:
        return principal.title


def update_object(obj, context):
    """Update one object."""
    creators = zope.dublincore.interfaces.IZopeDublinCore(obj).creators
    if not len(creators):
        return
    editor_storage = icemac.addressbook.metadata.interfaces.IEditor(obj)
    editor_storage.creator = principal_id_to_title(context, creators[0], obj)
    editor_storage.modifier = principal_id_to_title(context, creators[-1], obj)


def update_recursively(object, context, depth):
    """Do the metadata update for an object and its children."""
    depth += 1
    if depth > MAX_DEPTH:
        return
    # update object
    if zope.annotation.interfaces.IAttributeAnnotatable.providedBy(object):
        update_object(object, context)
    # update children
    if zope.container.interfaces.IContainer.providedBy(object):
        for obj in object.values():
            update_recursively(obj, context, depth)
    # update children on attributes
    if not hasattr(object, '__dict__'):
        return
    for name, obj in object.__dict__.items():
        if (zope.container.interfaces.IContainer.providedBy(object) and
                not name.startswith('_')):
            # short cut, only the values on public attributes which
            # are containers need to be converted
            update_recursively(obj, context, depth)


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(addressbook):
    """Update additional metadata from existing dublincore metadata."""
    update_recursively(addressbook, addressbook, 0)

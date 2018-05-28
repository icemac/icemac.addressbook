import icemac.addressbook.generations.utils
import zope.component
import zope.principalannotation.interfaces


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(addressbook):
    """Copy global principal annotations to local ones."""
    global_ann = zope.component.getUtility(
        zope.principalannotation.interfaces.IPrincipalAnnotationUtility,
        context=addressbook.__parent__)
    local_ann = zope.component.getUtility(
        zope.principalannotation.interfaces.IPrincipalAnnotationUtility,
        context=addressbook)
    principals = zope.component.getUtility(
        zope.pluggableauth.interfaces.IAuthenticatorPlugin,
        name=u'icemac.addressbook.principals')

    for pid, ann in global_ann.annotations.items():
        if pid not in principals:
            # principal does not exist in this address book
            continue
        local_ann.annotations[pid] = ann

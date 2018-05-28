import icemac.addressbook.generations.utils
import zope.component
import zope.pluggableauth.interfaces
import zope.principalannotation.interfaces
import BTrees.OOBTree


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(addressbook):
    """Update preferences to new structure."""
    principals = zope.component.getUtility(
        zope.pluggableauth.interfaces.IAuthenticatorPlugin,
        name=u'icemac.addressbook.principals')
    principal_annotations = zope.component.getUtility(
        zope.principalannotation.interfaces.IPrincipalAnnotationUtility)
    for pid in principals.keys():
        prefs = principal_annotations.getAnnotationsById(pid).get(
            zope.preference.preference.pref_key, {})
        if 'personList' not in prefs:
            continue
        for key, value in prefs['personList'].items():
            if key == 'batch_size':
                parent_key = 'ab.personListTab'
            elif key in ['columns', 'order_by', 'sort_direction']:
                parent_key = 'ab.personLists'
            else:
                raise KeyError('Unkown pref key: %s' % key)
            if parent_key not in prefs:
                prefs[parent_key] = BTrees.OOBTree.OOBTree()
            prefs[parent_key][key] = value
        del prefs['personList']

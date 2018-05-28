from zope.principalannotation.interfaces import IPrincipalAnnotationUtility
import zope.component
import zope.component.hooks
import zope.generations.utility


def evolve(context):
    """Remove global principal annotations utility.

    Data was migrated in the previous generation.

    """
    root_folder = zope.generations.utility.getRootFolder(context)
    try:
        old_site = zope.component.hooks.getSite()
        zope.component.hooks.setSite(root_folder)

        util = zope.component.getUtility(IPrincipalAnnotationUtility)
        sm = root_folder.getSiteManager()
        assert sm.unregisterUtility(
            provided=IPrincipalAnnotationUtility) is True
        del util.__parent__[util.__name__]
    finally:
        zope.component.hooks.setSite(old_site)

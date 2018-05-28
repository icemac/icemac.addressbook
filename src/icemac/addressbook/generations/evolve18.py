import zodbupdate.update


zaaa = "zope.app.authentication.authentication "
zaai = "zope.app.authentication.interfaces "
zaap = "zope.app.authentication.principalfolder "
zaas = "zope.app.authentication.session "
zaci = "zope.app.container.interfaces "
zacs = "zope.app.component.site "
zp = "zope.pluggableauth"


renames = {
    "zope.app.catalog.catalog Catalog": "zope.catalog.catalog Catalog",
    "zope.app.intid IntIds": "zope.intid IntIds",
    zaaa + "PluggableAuthentication": zp + " PluggableAuthentication",
    zaai + "IAuthenticatorPlugin": zp + ".interfaces IAuthenticatorPlugin",
    zaap + "PrincipalFolder": zp + ".plugins.principalfolder PrincipalFolder",
    zaas + "SessionCredentials": zp + ".plugins.session SessionCredentials",
    zaci + "IContained": "zope.container.interfaces IContained",
    zacs + "LocalSiteManager": "zope.site.site LocalSiteManager",
    zacs + "SiteManagementFolder": "zope.site.site SiteManagementFolder",
    zacs + "_LocalAdapterRegistry": "zope.site.site _LocalAdapterRegistry",
}


def evolve(context):
    """Update instances made from classes of from zope.app.* packages to ...

    ... their zope.* equivalents.

    """
    storage = context.connection._storage
    zodbupdate.update.Updater(storage, renames=renames, debug=True)()

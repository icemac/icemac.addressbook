# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.entities
import icemac.addressbook.file.interfaces
import icemac.addressbook.interfaces
import icemac.addressbook.keyword
import icemac.addressbook.orderstorage
import icemac.addressbook.preferences.default
import icemac.addressbook.utils
import zc.catalog.catalogindex
import zope.app.appsetup.bootstrap
import zope.app.authentication.authentication
import zope.app.authentication.interfaces
import zope.app.authentication.principalfolder
import zope.authentication.interfaces
import zope.catalog.catalog
import zope.catalog.interfaces
import zope.component
import zope.container.btree
import zope.container.interfaces
import zope.interface
import zope.intid
import zope.intid.interfaces
import zope.location
import zope.location.interfaces
import zope.schema.fieldproperty
import zope.site.site


class AddressBook(zope.container.btree.BTreeContainer,
                  zope.site.site.SiteManagerContainer):
    "An address book."

    zope.interface.implements(icemac.addressbook.interfaces.IAddressBook)

    entities = None
    importer = None
    keywords = None
    principals = None
    orders = None

    title = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IAddressBook['title'])

    def __repr__(self):
        return "<AddressBook %r (%r)>" % (self.__name__, self.title)

address_book_entity = icemac.addressbook.entities.create_entity(
    _(u'address book'), icemac.addressbook.interfaces.IAddressBook, AddressBook)


def create_and_register(addressbook, attrib_name, class_, interface, name=''):
    """Create an object on an attribute and register it as local utility."""
    if getattr(addressbook, attrib_name) is not None:
        return
    site_mgr = addressbook.getSiteManager()
    obj = icemac.addressbook.utils.create_obj(class_)
    setattr(addressbook, attrib_name, obj)
    zope.location.locate(obj, addressbook, '++attribute++'+attrib_name)
    site_mgr.registerUtility(obj, interface, name=name)


@zope.component.adapter(
    icemac.addressbook.interfaces.IAddressBook,
    zope.container.interfaces.IObjectAddedEvent)
def create_address_book_infrastructure(addressbook, event=None):
    """Create initial infrastructure or update existing infrastructure to
    current requirements (using generation)."""
    # add site manager
    if not zope.location.interfaces.ISite.providedBy(addressbook):
        site_manager = zope.site.site.LocalSiteManager(addressbook)
        addressbook.setSiteManager(site_manager)

    # add keywords container
    create_and_register(
        addressbook, 'keywords', icemac.addressbook.keyword.KeywordContainer,
        icemac.addressbook.interfaces.IKeywords)

    # add principals folder
    create_and_register(
        addressbook, 'principals',
        zope.app.authentication.principalfolder.PrincipalFolder,
        zope.app.authentication.interfaces.IAuthenticatorPlugin,
        name=u'icemac.addressbook.principals')

    # add entities utility
    create_and_register(
        addressbook, 'entities',
        icemac.addressbook.entities.PersistentEntities,
        icemac.addressbook.interfaces.IEntities)

    # add order storage utility
    create_and_register(
        addressbook, 'orders',
        icemac.addressbook.orderstorage.OrderStorage,
        icemac.addressbook.interfaces.IOrderStorage)

    def add_entity_to_order(iface):
        addressbook.orders.add(
            icemac.addressbook.interfaces.IEntity(iface).name,
            icemac.addressbook.interfaces.ENTITIES)

    add_entity_to_order(icemac.addressbook.interfaces.IAddressBook)
    add_entity_to_order(icemac.addressbook.interfaces.IPerson)
    add_entity_to_order(icemac.addressbook.interfaces.IPostalAddress)
    add_entity_to_order(icemac.addressbook.interfaces.IPhoneNumber)
    add_entity_to_order(icemac.addressbook.interfaces.IEMailAddress)
    add_entity_to_order(icemac.addressbook.interfaces.IHomePageAddress)
    add_entity_to_order(icemac.addressbook.file.interfaces.IFile)
    add_entity_to_order(icemac.addressbook.interfaces.IKeyword)

    add_more_addressbook_infrastructure(addressbook, addressbook)


@icemac.addressbook.utils.set_site
def add_more_addressbook_infrastructure(addressbook):
    "Add more infrastructure which depends on addressbook set as site."
    # intid utility
    if not icemac.addressbook.utils.utility_locally_registered(
            addressbook, zope.intid.interfaces.IIntIds):
        intids = zope.app.appsetup.bootstrap.ensureUtility(
            addressbook, zope.intid.interfaces.IIntIds, '', zope.intid.IntIds)

    # catalog
    if icemac.addressbook.utils.utility_locally_registered(
            addressbook, zope.catalog.interfaces.ICatalog):
        catalog = zope.component.queryUtility(zope.catalog.interfaces.ICatalog)
    else:
        # add catalog
        catalog = zope.app.appsetup.bootstrap.ensureUtility(
            addressbook, zope.catalog.interfaces.ICatalog, '',
            zope.catalog.catalog.Catalog)

    # indexes
    if 'keywords' not in catalog:
        catalog['keywords'] = zc.catalog.catalogindex.SetIndex(
            'get_titles', icemac.addressbook.interfaces.IKeywordTitles,
            field_callable=True)

    # authenticator (PAU)
    if not icemac.addressbook.utils.utility_locally_registered(
            addressbook, zope.authentication.interfaces.IAuthentication):
        pau = zope.app.appsetup.bootstrap.ensureUtility(
            addressbook, zope.authentication.interfaces.IAuthentication, '',
            zope.app.authentication.authentication.PluggableAuthentication)
        pau.credentialsPlugins = (u'No Challenge if Authenticated',
                                  u'Session Credentials',)
        pau.authenticatorPlugins = (u'icemac.addressbook.principals',)

    # default preferences
    icemac.addressbook.preferences.default.add(addressbook)

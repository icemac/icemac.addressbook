# -*- coding: utf-8 -*-
# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import _
import grokcore.component
import icemac.addressbook.entities
import icemac.addressbook.file.interfaces
import icemac.addressbook.interfaces
import icemac.addressbook.keyword
import icemac.addressbook.orderstorage
import icemac.addressbook.preferences.default
import icemac.addressbook.utils
import zc.catalog.catalogindex
import zope.app.appsetup.bootstrap
import zope.authentication.interfaces
import zope.catalog.catalog
import zope.catalog.interfaces
import zope.catalog.text
import zope.component
import zope.container.btree
import zope.container.interfaces
import zope.event
import zope.index.text.lexicon
import zope.interface
import zope.intid
import zope.intid.interfaces
import zope.location
import zope.location.interfaces
import zope.pluggableauth.authentication
import zope.pluggableauth.interfaces
import zope.pluggableauth.plugins.principalfolder
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
    _(u'address book'),
    icemac.addressbook.interfaces.IAddressBook, AddressBook)


def create_and_register(addressbook, attrib_name, class_, interface, name=''):
    """Create an object on an attribute and register it as local utility."""
    if getattr(addressbook, attrib_name) is not None:
        return
    site_mgr = addressbook.getSiteManager()
    obj = icemac.addressbook.utils.create_obj(class_)
    setattr(addressbook, attrib_name, obj)
    zope.location.locate(obj, addressbook, '++attribute++' + attrib_name)
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
        zope.pluggableauth.plugins.principalfolder.PrincipalFolder,
        zope.pluggableauth.interfaces.IAuthenticatorPlugin,
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
    add_entity_to_order(icemac.addressbook.interfaces.IPersonDefaults)
    add_entity_to_order(icemac.addressbook.interfaces.IPostalAddress)
    add_entity_to_order(icemac.addressbook.interfaces.IPhoneNumber)
    add_entity_to_order(icemac.addressbook.interfaces.IEMailAddress)
    add_entity_to_order(icemac.addressbook.interfaces.IHomePageAddress)
    add_entity_to_order(icemac.addressbook.file.interfaces.IFile)
    add_entity_to_order(icemac.addressbook.interfaces.IKeyword)

    zope.event.notify(AddressBookCreated(addressbook))


class AddressBookCreated(object):
    """Event which signales that an address book has been created.

    Subscribers can expect that the new address book is a site (but not set
    as such).
    """

    def __init__(self, address_book):
        self.address_book = address_book


@grokcore.component.subscribe(AddressBookCreated)
def add_more_addressbook_infrastructure(event):
    "Add more infrastructure which depends on addressbook set as site."
    addressbook = event.address_book
    try:
        old_site = zope.component.hooks.getSite()
        zope.component.hooks.setSite(addressbook)
        # intid utility
        if not icemac.addressbook.utils.utility_locally_registered(
                addressbook, zope.intid.interfaces.IIntIds):
            intids = zope.app.appsetup.bootstrap.ensureUtility(
                addressbook, zope.intid.interfaces.IIntIds, '',
                zope.intid.IntIds)

        # catalog
        if icemac.addressbook.utils.utility_locally_registered(
                addressbook, zope.catalog.interfaces.ICatalog):
            catalog = zope.component.queryUtility(
                zope.catalog.interfaces.ICatalog)
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
        if 'name' not in catalog:
            catalog['name'] = zope.catalog.text.TextIndex(
                'get_name', icemac.addressbook.interfaces.IPersonName,
                field_callable=True,
                lexicon=zope.index.text.lexicon.Lexicon(
                    zope.index.text.lexicon.Splitter(),
                    zope.index.text.lexicon.CaseNormalizer()))

        # authenticator (PAU)
        if not icemac.addressbook.utils.utility_locally_registered(
                addressbook,
                zope.authentication.interfaces.IAuthentication):
            pau = zope.app.appsetup.bootstrap.ensureUtility(
                addressbook, zope.authentication.interfaces.IAuthentication,
                '',
                zope.pluggableauth.authentication.PluggableAuthentication)
            pau.credentialsPlugins = (u'No Challenge if Authenticated',
                                      u'Flashed Session Credentials',)
            pau.authenticatorPlugins = (u'icemac.addressbook.principals',)

        # default preferences
        icemac.addressbook.preferences.default.add(addressbook)
    finally:
        zope.component.hooks.setSite(old_site)

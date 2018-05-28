# -*- coding: utf-8 -*-
from icemac.addressbook.interfaces import IPerson
import datetime
import icemac.addressbook.conftest
import icemac.addressbook.testing
import pytest
import transaction
import zope.component.hooks


# Fixtures to set-up infrastructure which are usable in tests:

@pytest.yield_fixture(scope='function')
def search_data(searchDataS):
    """Provide predefined search data, see `searchDataS`."""
    for connection in icemac.addressbook.testing.pyTestStackDemoStorage(
            searchDataS.zodb, 'search_data'):
        for address_book in icemac.addressbook.testing.site(connection):
            yield address_book


@pytest.yield_fixture(scope='function')
def person_with_field_data(personWithFieldDataS):
    """Provide predefined person data, see `personWithFieldDataS`."""
    for connection in icemac.addressbook.testing.pyTestStackDemoStorage(
            personWithFieldDataS.zodb, 'PersonWithFieldFunction'):
        yield connection


# Infrastructure fixtures

@pytest.yield_fixture(scope='session')
def searchDataS(
        addressBookS, KeywordFactory, PersonFactory, FullPersonFactory):
    """Create base data used in search tests."""
    for connection in icemac.addressbook.testing.pyTestStackDemoStorage(
            addressBookS, 'SearchSession'):
        for address_book in icemac.addressbook.testing.site(connection):
            KeywordFactory(address_book, u'work')
            KeywordFactory(address_book, u'anyone else')
            # person objects are not returned as addressBookConnectionF
            # puts a DemoStorage around the storage.
            FullPersonFactory(address_book, u'Hohmuth', keywords=[u'friends'])
            FullPersonFactory(
                address_book, u'Koch', keywords=[u'family', u'church'],
                birth_date=datetime.date(1952, 1, 24), notes=u'father-in-law')
            FullPersonFactory(
                address_book, u'Velleuer', keywords=[u'family', u'church'])
            FullPersonFactory(
                address_book, u'Liebig', keywords=[u'church'],
                notes=u'family')
            PersonFactory(address_book, u'Tester', first_name=u'Liese',
                          birth_date=datetime.date(1976, 11, 15))
            transaction.commit()
        yield connection


@pytest.yield_fixture(scope='session')
def personWithFieldDataS(
        addressBookS, FullPersonFactory, PostalAddressFactory, KeywordFactory,
        PhoneNumberFactory, EMailAddressFactory, HomepageAddressFactory,
        FieldFactory):
    """Create base data used in person tests."""
    for connection in icemac.addressbook.testing.pyTestStackDemoStorage(
            addressBookS, 'SearchSession'):
        address_book = connection.rootFolder['ab']
        with zope.component.hooks.site(address_book):
            field_name = FieldFactory(
                address_book, IPerson, 'TextLine', u'foobar').__name__
            icemac.addressbook.conftest._create_person(
                address_book, FullPersonFactory, PostalAddressFactory,
                KeywordFactory, PhoneNumberFactory, EMailAddressFactory,
                HomepageAddressFactory, **{field_name: u'my value'})
            yield connection

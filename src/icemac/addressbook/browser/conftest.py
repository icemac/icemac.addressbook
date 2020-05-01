# -*- coding: utf-8 -*-
from icemac.addressbook.interfaces import IPerson
import icemac.addressbook.testing
import pytest
import zope.component.hooks


# Fixtures to set-up infrastructure which are usable in tests,
# see also in ./fixtures.py (which are imported via src/../conftest.py):

@pytest.yield_fixture(scope='function')
def person_with_field_data(personWithFieldDataS):
    """Provide predefined person data, see `personWithFieldDataS`."""
    for connection in icemac.addressbook.testing.pyTestStackDemoStorage(
            personWithFieldDataS.zodb, 'PersonWithFieldFunction'):
        yield connection


# Infrastructure fixtures

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

# -*- coding: utf-8 -*-
import datetime
import decimal
from icemac.addressbook.interfaces import IEntityOrder, IEntity, IPhoneNumber
from icemac.addressbook.interfaces import IPerson, IPostalAddress
import icemac.addressbook.export.interfaces
import icemac.addressbook.export.xls.simple
import pytest
import xlrd
import zope.component
import zope.interface.verify


@pytest.fixture(scope='function')
def user_defined_fields_data(
        address_book, FieldFactory, FullPersonFactory, PhoneNumberFactory,
        PostalAddressFactory):
    """Fixture setting up the test data for user defined fields tests."""
    FieldFactory(address_book, IPerson, u'Bool', u'photo permission?')
    FieldFactory(address_book, IPerson, u'Datetime', u'last seen')
    FieldFactory(address_book, IPostalAddress, u'Choice', u'state',
                 values=[u'Sachsen', u'Sachsen-Anhalt', u'Brandenburg'])
    FieldFactory(address_book, IPostalAddress, u'Int', u'number of letters')
    FieldFactory(address_book, IPhoneNumber, u'Decimal', u'cost per minute')
    FieldFactory(address_book, IPhoneNumber, u'Text', u'mail box text')

    liebig = FullPersonFactory(
        address_book, u'Liebig',
        **{'person__first_name': u'B.',
           'person__Field-1': True,
           'person__Field-2': datetime.datetime(2009, 11, 1, 14, 1),
           'postal__city': u'Testhausen',
           'postal__Field-3': u'Sachsen-Anhalt',
           'postal__Field-4': 3,
           'phone__number': u'01234-5678-90',
           'phone__Field-5': decimal.Decimal('1.421'),
           'phone__Field-6': 'I am not here, leave a message, beep.'})
    howitz = FullPersonFactory(
        address_book, u'Howitz',
        **{'person__Field-1': False,
           'postal__city': u'Hettstedt',
           'postal__Field-3': u'Brandenburg'})

    # Let's create some additional phone numbers and postal addresses which
    # do not show up in defaults export but in complete export:
    PhoneNumberFactory(liebig, **{'Field-5': decimal.Decimal('1e2')})
    PhoneNumberFactory(liebig, **{'number': u'+49-3453-23434',
                                  'Field-5': decimal.Decimal('28')})
    PostalAddressFactory(howitz, **{'zip': u'00001', 'Field-4': 123456})
    return liebig, howitz


def test_simple__XLSExport__1():
    """`XLSExport` conforms to `IExporter`."""
    assert zope.interface.verify.verifyObject(
        icemac.addressbook.export.interfaces.IExporter,
        icemac.addressbook.export.xls.simple.XLSExport([], None))


def test_simple__DefaultsExport__1():
    """`DefaultsExport` conforms to `IExporter`."""
    assert zope.interface.verify.verifyObject(
        icemac.addressbook.export.interfaces.IExporter,
        icemac.addressbook.export.xls.simple.DefaultsExport([], None))


def test_simple__DefaultsExport__2(person_data, PhoneNumberFactory):
    """Export personal data, *main* addresses and numbers to an XLS file."""
    person = person_data['Person']
    # Additional phone numbers which does not show up in the export.
    PhoneNumberFactory(person, number=u'017612345678')
    export = icemac.addressbook.export.xls.simple.DefaultsExport(
        [person]).export()
    xls_workbook = xlrd.open_workbook(file_contents=export)
    assert [u'Address book - Export'] == xls_workbook.sheet_names()
    work_sheet_0 = xls_workbook.sheet_by_index(0)
    assert (3, 13) == (work_sheet_0.nrows, work_sheet_0.ncols)
    assert [
        [u'person',
         '',
         '',
         '',
         '',
         u'postal address',
         '',
         '',
         '',
         '',
         u'phone number',
         u'e-mail address',
         u'home page address'],
        [u'first name',
         u'last name',
         u'birth date',
         u'keywords',
         u'notes',
         u'address prefix',
         u'street',
         u'city',
         u'zip',
         u'country',
         u'number',
         u'e-mail address',
         u'URL'],
        [u'Petra',
         u'Tester',
         '',
         u'family, church',
         '',
         u'c/o Mama',
         u'Demoweg 23',
         u'Testhausen',
         u'88888',
         u'Austria',
         u'+4901767654321',
         u'petra@example.com',
         u'http://petra.example.com']] == [work_sheet_0.row_values(rx)
                                           for rx in range(work_sheet_0.nrows)]


def test_simple__DefaultsExport__3(address_book):
    """`DefaultsExport` returns a quite empty XLS file if nothing to export."""
    export = icemac.addressbook.export.xls.simple.DefaultsExport([]).export()
    xls_workbook = xlrd.open_workbook(file_contents=export)
    work_sheet_0 = xls_workbook.sheet_by_index(0)
    assert (2, 13) == (work_sheet_0.nrows, work_sheet_0.ncols)
    assert [
        [u'person',
         '',
         '',
         '',
         '',
         u'postal address',
         '',
         '',
         '',
         '',
         u'phone number',
         u'e-mail address',
         u'home page address'],
        [u'first name',
         u'last name',
         u'birth date',
         u'keywords',
         u'notes',
         u'address prefix',
         u'street',
         u'city',
         u'zip',
         u'country',
         u'number',
         u'e-mail address',
         u'URL']] == [work_sheet_0.row_values(rx)
                      for rx in range(work_sheet_0.nrows)]


def test_simple__DefaultsExport__4(address_book):
    """`DefaultsExport` respects the user defined entity sort order."""
    entity_order = zope.component.getUtility(IEntityOrder)
    entity_order.up(IEntity(IPhoneNumber), 1)

    export = icemac.addressbook.export.xls.simple.DefaultsExport([]).export()
    xls_workbook = xlrd.open_workbook(file_contents=export)
    work_sheet_0 = xls_workbook.sheet_by_index(0)
    assert (2, 13) == (work_sheet_0.nrows, work_sheet_0.ncols)
    assert [
        [u'person',
         '',
         '',
         '',
         '',
         u'phone number',
         u'postal address',
         '',
         '',
         '',
         '',
         u'e-mail address',
         u'home page address'],
        [u'first name',
         u'last name',
         u'birth date',
         u'keywords',
         u'notes',
         u'number',
         u'address prefix',
         u'street',
         u'city',
         u'zip',
         u'country',
         u'e-mail address',
         u'URL']] == [work_sheet_0.row_values(rx)
                      for rx in range(work_sheet_0.nrows)]


def test_simple__DefaultsExport__5(address_book):
    """`DefaultsExport` respects the user defined field sort order."""
    person_entity = IEntity(IPerson)
    person_entity.setFieldOrder(('last_name', 'first_name'))

    export = icemac.addressbook.export.xls.simple.DefaultsExport([]).export()
    xls_workbook = xlrd.open_workbook(file_contents=export)
    work_sheet_0 = xls_workbook.sheet_by_index(0)
    assert (2, 13) == (work_sheet_0.nrows, work_sheet_0.ncols)
    assert [
        [u'person',
         '',
         '',
         '',
         '',
         u'postal address',
         '',
         '',
         '',
         '',
         u'phone number',
         u'e-mail address',
         u'home page address'],
        [u'last name',
         u'first name',
         u'birth date',
         u'keywords',
         u'notes',
         u'address prefix',
         u'street',
         u'city',
         u'zip',
         u'country',
         u'number',
         u'e-mail address',
         u'URL']] == [work_sheet_0.row_values(rx)
                      for rx in range(work_sheet_0.nrows)]


def test_simple__DefaultsExport__6(user_defined_fields_data):
    """`DefaultsExport` exports user defined fields alike other fields."""
    export = icemac.addressbook.export.xls.simple.DefaultsExport(
        user_defined_fields_data).export()
    xls_workbook = xlrd.open_workbook(file_contents=export)
    work_sheet_0 = xls_workbook.sheet_by_index(0)
    assert (4, 19) == (work_sheet_0.nrows, work_sheet_0.ncols)
    assert [
        [u'person',
         '',
         '',
         '',
         '',
         '',
         '',
         u'postal address',
         '',
         '',
         '',
         '',
         '',
         '',
         u'phone number',
         '',
         '',
         u'e-mail address',
         u'home page address'],
        [u'first name',
         u'last name',
         u'birth date',
         u'keywords',
         u'notes',
         u'photo permission?',
         u'last seen',
         u'address prefix',
         u'street',
         u'city',
         u'zip',
         u'country',
         u'number of letters',
         u'state',
         u'number',
         u'cost per minute',
         u'mail box text',
         u'e-mail address',
         u'URL'],
        [u'B.',
         u'Liebig',
         '',
         '',
         '',
         1,
         40118.584027777775,
         '',
         '',
         u'Testhausen',
         '',
         u'Germany',
         3.0,
         u'Sachsen-Anhalt',
         u'01234-5678-90',
         1.421,
         u'I am not here, leave a message, beep.',
         '',
         ''],
        ['',
         u'Howitz',
         '',
         '',
         '',
         0,
         '',
         '',
         '',
         u'Hettstedt',
         '',
         u'Germany',
         '',
         u'Brandenburg',
         '',
         '',
         '',
         '',
         '']] == [work_sheet_0.row_values(rx)
                  for rx in range(work_sheet_0.nrows)]


def test_simple__DefaultsExport__7(address_book):
    """It respects the customized pre-defined field labels."""
    first_name_field = icemac.addressbook.interfaces.IPersonName['first_name']
    street_field = icemac.addressbook.interfaces.IPostalAddress['street']

    customization = icemac.addressbook.interfaces.IFieldCustomization(
        address_book)
    customization.set_value(first_name_field, u'label', u'Christian name')
    customization.set_value(street_field, u'label', u'street and house number')

    export = icemac.addressbook.export.xls.simple.DefaultsExport([]).export()
    xls_workbook = xlrd.open_workbook(file_contents=export)
    work_sheet_0 = xls_workbook.sheet_by_index(0)
    assert (2, 13) == (work_sheet_0.nrows, work_sheet_0.ncols)
    assert [
        [u'person',
         u'',
         u'',
         u'',
         u'',
         u'postal address',
         u'',
         u'',
         u'',
         u'',
         u'phone number',
         u'e-mail address',
         u'home page address'],
        [u'Christian name',
         u'last name',
         u'birth date',
         u'keywords',
         u'notes',
         u'address prefix',
         u'street and house number',
         u'city',
         u'zip',
         u'country',
         u'number',
         u'e-mail address',
         u'URL']] == [work_sheet_0.row_values(rx)
                      for rx in range(work_sheet_0.nrows)]


def test_simple__CompleteExport__1():
    """`CompleteExport` conforms to `IExporter`."""
    assert zope.interface.verify.verifyObject(
        icemac.addressbook.export.interfaces.IExporter,
        icemac.addressbook.export.xls.simple.CompleteExport([], None))


def test_simple__CompleteExport__2(person_data):
    """Export personal data, all addresses and numbers to an XLS file."""
    person = person_data['Person']
    export = icemac.addressbook.export.xls.simple.CompleteExport(
        [person]).export()
    xls_workbook = xlrd.open_workbook(file_contents=export)
    assert [u'Address book - Export'] == xls_workbook.sheet_names()
    work_sheet_0 = xls_workbook.sheet_by_index(0)
    assert (3, 21) == (work_sheet_0.nrows, work_sheet_0.ncols)
    assert ([
        [u'person',
         '',
         '',
         '',
         '',
         u'main postal address',
         '',
         '',
         '',
         '',
         u'other postal address',
         '',
         '',
         '',
         '',
         u'main phone number',
         u'other phone number',
         u'main e-mail address',
         u'other e-mail address',
         u'main home page address',
         u'other home page address'],
        [u'first name',
         u'last name',
         u'birth date',
         u'keywords',
         u'notes',
         u'address prefix',
         u'street',
         u'city',
         u'zip',
         u'country',
         u'address prefix',
         u'street',
         u'city',
         u'zip',
         u'country',
         u'number',
         u'number',
         u'e-mail address',
         u'e-mail address',
         u'URL',
         u'URL'],
        [u'Petra',
         u'Tester',
         '',
         u'family, church',
         '',
         u'c/o Mama',
         u'Demoweg 23',
         u'Testhausen',
         u'88888',
         u'Austria',
         u'RST-Software',
         u'Forsterstraße 302a',
         u'Erfurt',
         u'98344',
         u'Germany',
         u'+4901767654321',
         u'+4901761234567',
         u'petra@example.com',
         u'pt@rst.example.edu',
         u'http://petra.example.com',
         u'http://www.rst.example.edu']] ==
        [work_sheet_0.row_values(rx)
         for rx in range(work_sheet_0.nrows)])


def test_simple__CompleteExport__3(address_book):
    """`CompleteExport` returns a quite empty XLS file if nothing to export."""
    export = icemac.addressbook.export.xls.simple.CompleteExport([]).export()
    xls_workbook = xlrd.open_workbook(file_contents=export)
    work_sheet_0 = xls_workbook.sheet_by_index(0)
    assert (2, 5) == (work_sheet_0.nrows, work_sheet_0.ncols)
    assert ([
        [u'person', '', '', '', ''],
        [u'first name', u'last name', u'birth date', u'keywords', u'notes']] ==
        [work_sheet_0.row_values(rx)
         for rx in range(work_sheet_0.nrows)])


def test_simple__CompleteExport__4(
        address_book, PersonFactory, PhoneNumberFactory):
    """`CompleteExport` respects the user defined entity sort order."""
    person = PersonFactory(address_book, u'Tester')
    PhoneNumberFactory(person, number=u'+48-123-321', set_as_default=True)
    PhoneNumberFactory(person, number=u'+321-48-84', set_as_default=False)

    entity_order = zope.component.getUtility(IEntityOrder)
    phone_number_entity = IEntity(IPhoneNumber)
    entity_order.up(phone_number_entity, 1)

    export = icemac.addressbook.export.xls.simple.CompleteExport(
        [person]).export()
    xls_workbook = xlrd.open_workbook(file_contents=export)
    work_sheet_0 = xls_workbook.sheet_by_index(0)
    assert (3, 7) == (work_sheet_0.nrows, work_sheet_0.ncols)
    assert ([
        [u'person',
         '',
         '',
         '',
         '',
         u'main phone number',
         u'other phone number'],
        [u'first name',
         u'last name',
         u'birth date',
         u'keywords',
         u'notes',
         u'number',
         u'number'],
        ['',
         u'Tester',
         '',
         '',
         '',
         u'+48-123-321',
         u'+321-48-84']] == [work_sheet_0.row_values(rx)
                             for rx in range(work_sheet_0.nrows)])


def test_simple__CompleteExport__5(address_book, ):
    """`CompleteExport` respects the user defined field sort order."""
    person_entity = IEntity(IPerson)
    person_entity.setFieldOrder(('last_name', 'first_name'))

    export = icemac.addressbook.export.xls.simple.CompleteExport([]).export()
    xls_workbook = xlrd.open_workbook(file_contents=export)
    work_sheet_0 = xls_workbook.sheet_by_index(0)
    assert (2, 5) == (work_sheet_0.nrows, work_sheet_0.ncols)
    assert ([
        [u'person',
         '',
         '',
         '',
         ''],
        [u'last name',
         u'first name',
         u'birth date',
         u'keywords',
         u'notes']] == [work_sheet_0.row_values(rx)
                        for rx in range(work_sheet_0.nrows)])


def test_simple__CompleteExport__6(user_defined_fields_data):
    """`CompleteExport` exports user defined fields alike other fields."""
    export = icemac.addressbook.export.xls.simple.CompleteExport(
        user_defined_fields_data).export()
    xls_workbook = xlrd.open_workbook(file_contents=export)
    work_sheet_0 = xls_workbook.sheet_by_index(0)
    assert (4, 32) == (work_sheet_0.nrows, work_sheet_0.ncols)
    assert [
        [u'person',
         '',
         '',
         '',
         '',
         '',
         '',
         u'main postal address',
         '',
         '',
         '',
         '',
         '',
         '',
         u'other postal address',
         '',
         '',
         '',
         '',
         '',
         '',
         u'main phone number',
         '',
         '',
         u'other phone number',
         '',
         '',
         u'other phone number',
         '',
         '',
         u'main e-mail address',
         u'main home page address'],
        [u'first name',
         u'last name',
         u'birth date',
         u'keywords',
         u'notes',
         u'photo permission?',
         u'last seen',
         u'address prefix',
         u'street',
         u'city',
         u'zip',
         u'country',
         u'number of letters',
         u'state',
         u'address prefix',
         u'street',
         u'city',
         u'zip',
         u'country',
         u'number of letters',
         u'state',
         u'number',
         u'cost per minute',
         u'mail box text',
         u'number',
         u'cost per minute',
         u'mail box text',
         u'number',
         u'cost per minute',
         u'mail box text',
         u'e-mail address',
         u'URL'],
        [u'B.',
         u'Liebig',
         '',
         '',
         '',
         1,
         40118.584027777775,
         '',
         '',
         u'Testhausen',
         '',
         u'Germany',
         3.0,
         u'Sachsen-Anhalt',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         u'01234-5678-90',
         1.421,
         u'I am not here, leave a message, beep.',
         '',
         100.0,
         '',
         u'+49-3453-23434',
         28.0,
         '',
         '',
         ''],
        ['',
         u'Howitz',
         '',
         '',
         '',
         0,
         '',
         '',
         '',
         u'Hettstedt',
         '',
         u'Germany',
         '',
         u'Brandenburg',
         '',
         '',
         '',
         u'00001',
         u'Germany',
         123456.0,
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         '']] == [work_sheet_0.row_values(rx)
                  for rx in range(work_sheet_0.nrows)]

# -*- coding: utf-8 -*-
import xlrd
from icemac.addressbook.interfaces import IPerson


def create_person(
        field_title, keyword_title, address_book, FieldFactory,
        FullPersonFactory, PostalAddressFactory):
    """Create a person in the address book as needed by the tests."""
    field_name = FieldFactory(
        address_book, IPerson, u'Bool', field_title).__name__
    person = FullPersonFactory(
        address_book, u'Liebig', postal__city=u'Testhausen',
        keywords=[keyword_title], **{field_name: True})
    # Let's create an additional postal address which does not show up in
    # the defaults export but in complete export:
    PostalAddressFactory(person, zip=u'00001')


def test_xls__DefaultsExport__1(search_data, browser):
    """`DefaultsExport` can export the values of the default data as XLS."""
    browser.login('visitor')
    browser.keyword_search('church', 'XLS export main')
    assert 'application/vnd.ms-excel' == browser.headers['Content-Type']
    assert ('attachment; filename=addressbook_export.xls' ==
            browser.headers['Content-Disposition'])
    xls_workbook = xlrd.open_workbook(file_contents=browser.contents)
    assert [u'Address book - Export'] == xls_workbook.sheet_names()
    work_sheet_0 = xls_workbook.sheet_by_index(0)
    assert (5, 13) == (work_sheet_0.nrows, work_sheet_0.ncols)
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
        ['',
         u'Koch',
         19017.0,
         u'family, church',
         u'father-in-law',
         '',
         '',
         '',
         '',
         u'Germany',
         '',
         '',
         ''],
        ['',
         u'Liebig',
         '',
         u'church',
         u'family',
         '',
         '',
         '',
         '',
         u'Germany',
         '',
         '',
         ''],
        ['',
         u'Velleuer',
         '',
         u'family, church',
         '',
         '',
         '',
         '',
         '',
         u'Germany',
         '',
         '',
         '']] == [work_sheet_0.row_values(rx)
                  for rx in range(work_sheet_0.nrows)]


def test_xls__DefaultsExport__2(search_data, browser):
    """`DefaultsExport` only exports the selected persons."""
    browser.login('visitor')
    browser.keyword_search('church')
    browser.getControl('Apply on selected persons').displayValue = [
        'XLS export main']
    browser.getControl(
        name='persons:list').getControl(value="Person-2").selected = False
    browser.getControl(name='form.buttons.apply').click()
    xls_workbook = xlrd.open_workbook(file_contents=browser.contents)
    work_sheet_0 = xls_workbook.sheet_by_index(0)
    assert (4, 13) == (work_sheet_0.nrows, work_sheet_0.ncols)
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
        ['',
         u'Liebig',
         '',
         u'church',
         u'family',
         '',
         '',
         '',
         '',
         u'Germany',
         '',
         '',
         ''],
        ['',
         u'Velleuer',
         '',
         u'family, church',
         '',
         '',
         '',
         '',
         '',
         u'Germany',
         '',
         '',
         '']] == [work_sheet_0.row_values(rx)
                  for rx in range(work_sheet_0.nrows)]


def test_xls__DefaultsExport__3(
        address_book, FieldFactory, FullPersonFactory, PostalAddressFactory,
        browser):
    """`DefaultsExport` exports user defined fields like other fields."""
    create_person(u'photo permission?', u'church', address_book, FieldFactory,
                  FullPersonFactory, PostalAddressFactory)
    browser.login('visitor')
    browser.open(browser.SEARCH_URL)
    # We choose the keyword search as it has export abilities:
    browser.getLink('Keyword search').click()
    browser.getControl('keywords').displayValue = ['church']
    browser.getControl('Search').click()
    # The export produces an XLS file:
    browser.getControl('Apply on selected persons').displayValue = [
        'XLS export main']
    browser.getControl(name='form.buttons.apply').click()
    assert 'application/vnd.ms-excel' == browser.headers['Content-Type']
    xls_workbook = xlrd.open_workbook(file_contents=browser.contents)
    work_sheet_0 = xls_workbook.sheet_by_index(0)
    assert (3, 14) == (work_sheet_0.nrows, work_sheet_0.ncols)
    assert [
        [u'person',
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
         u'phone number',
         u'e-mail address',
         u'home page address'],
        [u'first name',
         u'last name',
         u'birth date',
         u'keywords',
         u'notes',
         u'photo permission?',
         u'address prefix',
         u'street',
         u'city',
         u'zip',
         u'country',
         u'number',
         u'e-mail address',
         u'URL'],
        ['',
         u'Liebig',
         '',
         u'church',
         '',
         True,
         '',
         '',
         u'Testhausen',
         '',
         u'Germany',
         '',
         '',
         '']] == [work_sheet_0.row_values(rx)
                  for rx in range(work_sheet_0.nrows)]


def test_xls__DefaultsExport__4(
        translated_address_book, FieldFactory, FullPersonFactory,
        PostalAddressFactory, browser):
    """`DefaultsExport` translates field names into user's language."""
    create_person(u'Fotoerlaubnis?', u'Kirche', translated_address_book,
                  FieldFactory, FullPersonFactory, PostalAddressFactory)
    # As visitors are allowed to search and export, so we log in as a
    # visitor, to enable translation, we also send an accept-language
    # header:
    browser.login('visitor')
    browser.lang('de-DE')
    browser.open(browser.SEARCH_BY_KEYWORD_URL)
    browser.getControl('Schlagwörter').displayValue = ['Kirche']
    browser.getControl('Suchen').click()
    browser.getControl('Auf ausgewählte Personen anwenden').displayValue = [
        'bevorzugte']
    browser.getControl(name='form.buttons.apply').click()
    assert 'application/vnd.ms-excel' == browser.headers['Content-Type']
    xls_workbook = xlrd.open_workbook(file_contents=browser.contents)
    work_sheet_0 = xls_workbook.sheet_by_index(0)
    assert (3, 14) == (work_sheet_0.nrows, work_sheet_0.ncols)
    assert [
        [u'Person',
         '',
         '',
         '',
         '',
         '',
         u'Anschrift',
         '',
         '',
         '',
         '',
         u'Telefonnummer',
         u'E-Mail-Adresse',
         u'Homepage-Adresse'],
        [u'Vorname',
         u'Familienname',
         u'Geburtsdatum',
         u'Schlagwörter',
         u'Anmerkungen',
         u'Fotoerlaubnis?',
         u'Adresszusatz',
         u'Straße',
         u'Ort',
         u'PLZ',
         u'Land',
         u'Nummer',
         u'E-Mail-Adresse',
         u'URL'],
        ['',
         u'Liebig',
         '',
         u'Kirche',
         '',
         1,
         '',
         '',
         u'Testhausen',
         '',
         u'Deutschland',
         '',
         '',
         '']] == [work_sheet_0.row_values(rx)
                  for rx in range(work_sheet_0.nrows)]


def test_xls__CompleteExport__1(
        translated_address_book, FieldFactory, FullPersonFactory,
        PostalAddressFactory, browser):
    """`CompleteExport` translates field names into user's language."""
    create_person(u'Fotoerlaubnis?', u'Kirche', translated_address_book,
                  FieldFactory, FullPersonFactory, PostalAddressFactory)
    # The complete export is not really different from the main one:
    browser.login('visitor')
    browser.lang('de-DE')
    browser.open(browser.SEARCH_BY_KEYWORD_URL)
    browser.getControl('Schlagwörter').displayValue = ['Kirche']
    browser.getControl('Suchen').click()
    browser.getControl('Auf ausgewählte Personen anwenden').displayValue = [
        'vollständig']
    browser.getControl(name='form.buttons.apply').click()
    assert 'application/vnd.ms-excel' == browser.headers['Content-Type']
    xls_workbook = xlrd.open_workbook(file_contents=browser.contents)
    work_sheet_0 = xls_workbook.sheet_by_index(0)
    assert (3, 19) == (work_sheet_0.nrows, work_sheet_0.ncols)
    assert [
        [u'Person',
         '',
         '',
         '',
         '',
         '',
         u'bevorzugte Anschrift',
         '',
         '',
         '',
         '',
         u'weitere Anschrift',
         '',
         '',
         '',
         '',
         u'bevorzugte Telefonnummer',
         u'bevorzugte E-Mail-Adresse',
         u'bevorzugte Homepage-Adresse'],
        [u'Vorname',
         u'Familienname',
         u'Geburtsdatum',
         u'Schlagwörter',
         u'Anmerkungen',
         u'Fotoerlaubnis?',
         u'Adresszusatz',
         u'Straße',
         u'Ort',
         u'PLZ',
         u'Land',
         u'Adresszusatz',
         u'Straße',
         u'Ort',
         u'PLZ',
         u'Land',
         u'Nummer',
         u'E-Mail-Adresse',
         u'URL'],
        ['',
         u'Liebig',
         '',
         u'Kirche',
         '',
         1,
         '',
         '',
         u'Testhausen',
         '',
         u'Deutschland',
         '',
         '',
         '',
         u'00001',
         u'Deutschland',
         '',
         '',
         '']] == [work_sheet_0.row_values(rx)
                  for rx in range(work_sheet_0.nrows)]


def test_xls__CompleteExport__2(search_data, browser):
    """`CompleteExport` does not fail if no person is selected."""
    browser.login('visitor')
    browser.keyword_search('friends')
    browser.getControl('Apply on selected persons').displayValue = [
        'XLS export complete']
    browser.getControl(
        name='persons:list').getControl(value="Person").selected = False
    browser.getControl(name='form.buttons.apply').click()
    # When the user chooses no person for export a nearly empty sheet gets
    # exported.
    xls_workbook = xlrd.open_workbook(file_contents=browser.contents)
    work_sheet_0 = xls_workbook.sheet_by_index(0)
    assert (2, 5) == (work_sheet_0.nrows, work_sheet_0.ncols)
    assert [
        [u'person', '', '', '', ''],
        [u'first name',
         u'last name',
         u'birth date',
         u'keywords',
         u'notes']] == [work_sheet_0.row_values(rx)
                        for rx in range(work_sheet_0.nrows)]

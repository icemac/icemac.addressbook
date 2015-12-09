from icemac.addressbook.testing import set_modified
import zope.component
from zope.preference.interfaces import IDefaultPreferenceProvider


def test_metadata__MetadataGroup__1(address_book, FullPersonFactory, browser):
    """`MetadataGroup` shows the modification date of each entry."""
    # Change the modification dates to known values to show  that they are
    # independent.
    person = FullPersonFactory(address_book, u'Tester')
    set_modified(person, 2001, 1, 1)
    set_modified(person['PostalAddress'], 2002, 2, 2)
    set_modified(person['PhoneNumber'], 2003, 3, 3)
    set_modified(person['EMailAddress'], 2004, 4, 4)
    set_modified(person['HomePageAddress'], 2005, 5, 5)

    browser.login('visitor')
    browser.open(browser.PERSON_EDIT_URL)
    # The modification date of each entry is displayed:
    assert [
        '01/01/01 00:00',
        '02/02/02 00:00',
        '03/03/03 00:00',
        '04/04/04 00:00',
        '05/05/05 00:00'] == browser.etree.xpath(
        "//form/div/div/fieldset/fieldset/div[4]/div/span/text()")


def test_metadata__MetadataGroup__2(address_book, KeywordFactory, browser):
    """`MetadataGroup` normalizes times to time zone in prefs."""
    kw = KeywordFactory(address_book, u'foo')
    set_modified(kw, 2001, 1, 1)
    default_prefs = zope.component.getUtility(IDefaultPreferenceProvider)
    default_prefs.getDefaultPreferenceGroup('ab.timeZone').time_zone = (
        'Asia/Aden')

    browser.login('visitor')
    browser.open(browser.KEYWORD_EDIT_URL)
    assert '01/01/01 03:00' in browser.contents
    assert 'Modification Date (Asia/Aden)' in browser.contents
    assert 'Creation Date (Asia/Aden)' in browser.contents

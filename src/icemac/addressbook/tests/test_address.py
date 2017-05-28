from icemac.addressbook.address import HomePageAddress, PhoneNumber
from icemac.addressbook.address import PostalAddress, EMailAddress
from icemac.addressbook.address import default_attrib_name_to_entity
from icemac.addressbook.address import normalize_phone_number
from icemac.addressbook.interfaces import IEMailAddress, IPostalAddress, ITitle
from icemac.addressbook.interfaces import IHomePageAddress, IPhoneNumber
import pytest
import six
import zope.interface.verify


def test_address__PostalAddress__1():
    """`PostalAddress` fulfills the `IPostalAddress` interface."""
    zope.interface.verify.verifyObject(IPostalAddress, PostalAddress())


def test_address__EMailAddress__1():
    """`EMailAddress` fulfills the `IEMailAddress` interface."""
    zope.interface.verify.verifyObject(IEMailAddress, EMailAddress())


def test_address__HomePageAddress__1():
    """`HomePageAddress` fulfills the `IHomePageAddress` interface."""
    zope.interface.verify.verifyObject(IHomePageAddress, HomePageAddress())


def test_address__PhoneNumber__1():
    """`PhoneNumber` fulfills the `IPhoneNumber` interface."""
    zope.interface.verify.verifyObject(IPhoneNumber, PhoneNumber())


def test_address__default_attrib_name_to_entity__1(stubEntities):
    """`default_attrib_name_to_entity` raises a ValueError for unknown name."""
    with pytest.raises(ValueError):
        default_attrib_name_to_entity('foo')


def test_address__default_attrib_name_to_entity__2(stubEntities):
    """`default_attrib_name_to_entity` returns the entity for a known name."""
    assert stubEntities.duck == default_attrib_name_to_entity('default_duck')


def test_address__normalize_phone_number__1():
    """`normalize_phone_number` returns a normalized number unchanged."""
    assert '+491234567890' == normalize_phone_number('+491234567890', '+49')


def test_address__normalize_phone_number__2():
    """`normalize_phone_number` keeps only numbers and a leading plus sign."""
    assert '+491234567890' == normalize_phone_number(
        '+49 (1234) 5678 - 90X', '+49')


def test_address__normalize_phone_number__3():
    """`normalize_phone_number` replaces a leading '0' by the country code."""
    assert '+491234567891' == normalize_phone_number('01234/5678-91', '+49')


def test_address__normalize_phone_number__4():
    """`normalize_phone_number` replaces only the first '0' by country code."""
    assert '+491234507090' == normalize_phone_number('01234/5070-90', '+49')


def test_address__normalize_phone_number__5():
    """`normalize_phone_number` does not replace '0' on empty country code."""
    assert '01234567891' == normalize_phone_number('01234/5678-91', '')


def test_address__normalize_phone_number__6():
    """`normalize_phone_number` replaces leading '00' by plus sign.

    The country code is ignored in this case.
    """
    assert '+421234567891' == normalize_phone_number(
        '0042-1234/5678-91', '+49')


def test_address__normalize_phone_number__7():
    """`normalize_phone_number` replaces only leading '00' by plus sign."""
    assert '+421234007891' == normalize_phone_number(
        '0042-1234/0078-91', '+49')


def test_address__email_address_of_person__1(
        address_book, PersonFactory, EMailAddressFactory):
    """Adaption to IEMailAddress returns the default address of the person."""
    person = PersonFactory(address_book, u'Tester')
    EMailAddressFactory(person, u'tester@exmaple.com', set_as_default=False)
    EMailAddressFactory(person, u't@exmaple.net', set_as_default=True)
    assert u't@exmaple.net' == IEMailAddress(person).email


def test_address__email_address_of_person__2(address_book, PersonFactory):
    """Missing default email address leads to a TypeError."""
    person = PersonFactory(address_book, u'Tester')
    with pytest.raises(TypeError) as err:
        IEMailAddress(person)
    assert 'Could not adapt' == err.value[0]


def test_address__postal_address_title__1(zcmlS):
    """A really empty postal address has a title of 'none'."""
    pa = PostalAddress()
    pa.country = None  # reset default value of `Germany`
    assert u'none' == ITitle(pa)


def test_address__postal_address_title__2(zcmlS):
    """`postal_address_title` displays set parts of the address."""
    pa = PostalAddress()
    pa.street = u'Papa street 3 a'
    assert u'Papa street 3 a, Germany' == ITitle(pa)


def test_address__postal_address_title__3(zcmlS):
    """`postal_address_title` is able to render the full address."""
    pa = PostalAddress()
    pa.address_prefix = u'c/o Mama'
    pa.street = u'Papa street 3 a'
    pa.zip = u'12345'
    pa.city = u'Dingshausen'
    assert (u'c/o Mama, Papa street 3 a, 12345, Dingshausen, Germany' ==
            ITitle(pa))


def test_address__email_address_title__1(zcmlS):
    """An empty email address has a title of 'none'."""
    assert u'none' == ITitle(EMailAddress())


def test_address__email_address_title__2(zcmlS):
    """`email_address_title` renders the email address if set."""
    ea = EMailAddress()
    ea.email = u'tester@example.org'
    assert u'tester@example.org' == ITitle(ea)


def test_address__home_page_address_title__1(zcmlS):
    """An empty home page address has a title of 'none'."""
    assert u'none' == ITitle(HomePageAddress())


def test_address__home_page_address_title__2(zcmlS):
    """`home_page_address_title` renders the home page URL if set."""
    hp = HomePageAddress()
    hp.url = 'http://www.example.org'
    assert u'http://www.example.org' == ITitle(hp)
    assert isinstance(ITitle(hp), six.text_type)


def test_address__phone_number_title__1(zcmlS):
    """An empty phone number has a title of 'none'."""
    assert u'none' == ITitle(PhoneNumber())


def test_address__phone_number_title__2(zcmlS):
    """`phone_number_title` renders the home page URL if set."""
    n = PhoneNumber()
    n.number = u'+017912345678'
    assert u'+017912345678' == ITitle(n)

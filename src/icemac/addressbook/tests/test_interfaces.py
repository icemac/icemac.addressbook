# -*- coding: utf-8 -*-
import pytest
from icemac.addressbook.address import EMailAddress, HomePageAddress
from zope.schema.interfaces import ConstraintNotSatisfied, InvalidURI


@pytest.mark.parametrize('candidate', [
    u'asdfg',
    u'ich@',
    u'ich@goo@le.de',
    u'ich@local',
    u'ich@local..de',
    u'ich@local.de.'], ids=lambda x: str(x))
def test_interfaces__IEMailAddress__email__1(candidate):
    """The constraint on `email` refuses non-valid email addresses."""
    email_address = EMailAddress()
    with pytest.raises(ConstraintNotSatisfied):
        email_address.email = candidate


@pytest.mark.parametrize('candidate', [
    u'ich@example.org',
    u'ich+du@example.org',
    u'ich=du@example.org',
    u'ich_du@example.org',
    u'ich-du@example.org',
    u'ich+du@a.b.c.d.example.org',
    u'ich+du@example.museum',
    u'ich@ex-ample.de',
    u'ich@ex_ample.de',
    # Some examples from RFC 3696 (Note: not all examples from this RFC are
    # supported!):
    u'user+mailbox@example.com',
    u'customer/department=shipping@example.com',
    u'$A12345@example.com',
    u'!def!xyz%abc@example.com',
    u'_somename@example.com'], ids=lambda x: str(x))
def test_interfaces__IEMailAddress__email__2(candidate):
    """The constraint on `email` allows valid email addresses."""
    email_address = EMailAddress()
    email_address.email = candidate


@pytest.mark.parametrize('candidate', [
    'asdfg',
    'www.example.com'])
def test_interfaces__IHomePageAddress__url__1(candidate):
    """The constraint on `url` refuses non-valid URIs."""
    home_page_address = HomePageAddress()
    with pytest.raises(InvalidURI):
        home_page_address.url = candidate


@pytest.mark.parametrize('candidate', [
    'http://www.example.org',
    'http://www2.example.org',
    'http://a.b.c.d.example.org',
    'http://example.museum'])
def test_interfaces__IHomePageAddress__url__2(candidate):
    """The constraint on `url` allows valid URIs."""
    home_page_address = HomePageAddress()
    home_page_address.url = candidate

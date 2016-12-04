# -*- coding: utf-8 -*-
from icemac.addressbook.principals.interfaces import IPasswordFields
from icemac.addressbook.principals.interfaces import IPrincipal, IRoles
from icemac.addressbook.principals.principals import Principal, created
from icemac.addressbook.utils import create_obj
from zope.interface.verify import verifyObject
import icemac.addressbook.interfaces
import pytest


def test_principals__Principal__1(zcmlS):
    """It fulfills the `IPrincipal` interface."""
    principal = Principal()
    # We need to call the created event handler here, because the person
    # attribute is a descriptor wrapping the object verifyObject expects.
    created(principal, None)
    assert verifyObject(IPrincipal, principal)


def test_principals__Principal__2(zcmlS):
    """It fulfills the `IPasswordFields` interface."""
    principal = Principal()
    assert verifyObject(IPasswordFields, principal)


def test_principals__Principal__3(zcmlS):
    """It fulfills the `IRoles` interface."""
    principal = Principal()
    assert verifyObject(IRoles, principal)


def test_principals__Principal__person__1(address_book, FullPersonFactory):
    """It raises a ValueError if the `person` is set again."""
    principal = create_obj(Principal)
    person = FullPersonFactory(address_book, u'User')
    principal.person = person
    assert principal.person == person
    with pytest.raises(ValueError) as err:
        principal.person = None
    assert ('It is not possible to change the person on a principal.' ==
            str(err.value))


def test_principals__title__1(zcmlS):
    """It returns a default value if the principal has no person assigned."""
    principal = Principal()
    assert '<no person>' == icemac.addressbook.interfaces.ITitle(principal)

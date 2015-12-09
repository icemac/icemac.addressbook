# -*- coding: utf-8 -*-
from icemac.addressbook.principals.interfaces import IPasswordFields
from icemac.addressbook.principals.interfaces import IPrincipal, IRoles
from icemac.addressbook.principals.principals import Principal, created
from zope.interface.verify import verifyObject


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

from icemac.addressbook.interfaces import ITitle
import icemac.addressbook.interfaces
import zope.interface


def test_adapter__default_title__1(zcmlS):
    """It returns a string unchanged."""
    assert 'asdf' == ITitle('asdf')


def test_adapter__default_title__2(zcmlS):
    """It returns a unicode unchanged."""
    assert u'qwe' == ITitle(u'qwe')


def test_adapter__default_title__3(zcmlS):
    """It returns a the string representation of other objects."""
    assert ITitle(object()).startswith('<object object at 0x')


def test_adapter__exception_title__1(zcmlS):
    """It renders the exception manually instead of using str(exception).

    The latter is overwritten by Chameleon with a currently ugly and lengthy
    representation.
    """
    assert u'<KeyError(42,)>' == ITitle(KeyError(42))


def test_adapter__SchemaProvider_SchemaName__schema_name__1(zcmlS):
    """It is the name of the interface of the schema provider."""
    @zope.interface.implementer(icemac.addressbook.interfaces.ISchemaProvider)
    class Foo(object):
        schema = ITitle

    schema_name = icemac.addressbook.interfaces.ISchemaName(Foo()).schema_name
    assert 'ITitle' == schema_name
    assert isinstance(schema_name, unicode)


def test_adapter__Interface__schema_name__1(zcmlS):
    """It is the name of the interface."""
    schema_name = icemac.addressbook.interfaces.ISchemaName(ITitle).schema_name
    assert 'ITitle' == schema_name
    assert isinstance(schema_name, unicode)

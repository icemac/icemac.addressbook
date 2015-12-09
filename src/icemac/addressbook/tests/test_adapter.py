from icemac.addressbook.interfaces import ITitle


def test_adapter__default_title__1(zcmlS):
    """`default_title` returns a string unchanged."""
    assert 'asdf' == ITitle('asdf')


def test_adapter__default_title__2(zcmlS):
    """`default_title` returns a unicode unchanged."""
    assert u'qwe' == ITitle(u'qwe')


def test_adapter__default_title__3(zcmlS):
    """`default_title` returns a the string representation of other objects."""
    assert ITitle(object()).startswith('<object object at 0x')

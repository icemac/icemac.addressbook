from icemac.addressbook.catalog.serializer import FieldNoSerializer
from icemac.addressbook.catalog.serializer import FieldSerializer
import gocept.country.db
import pytest
import six
import zope.schema


class SerializableObject(object):
    """Test object for serialization tests."""

    text = u'asdf'
    number1 = 2411
    number2 = 1234.6789
    bytes = 'foobar'


def callSerializer(field_class_name, field_name, serializer):
    """Call a serializer on a specified field type."""
    field = getattr(zope.schema, field_class_name)(title=u'')
    field.__name__ = field_name
    result = serializer(field, SerializableObject())
    assert isinstance(result, six.text_type)
    return result


def test_serializer__FieldSerializer__1():
    """`FieldSerializer` converts TextLine to unicode."""
    assert u'asdf' == callSerializer('TextLine', 'text', FieldSerializer)


def test_serializer__FieldSerializer__2():
    """`FieldSerializer` converts Text to unicode."""
    assert u'asdf' == callSerializer('Text', 'text', FieldSerializer)


def test_serializer__FieldSerializer__3():
    """`FieldSerializer` converts Int to unicode."""
    assert u'2411' == callSerializer('Int', 'number1', FieldSerializer)


def test_serializer__FieldSerializer__4():
    """`FieldSerializer` converts Float to unicode."""
    assert u'1234.6789' == callSerializer('Float', 'number2', FieldSerializer)


def test_serializer__FieldNoSerializer__1():
    """`FieldSerializer` converts Float to unicode."""
    assert u'' == callSerializer('Bytes', 'bytes', FieldNoSerializer)


@pytest.mark.xfail
def test_serializer__ObjectSerializer__1(
        address_book, PersonFactory, PostalAddressFactory):
    """`ObjectSerializer` serializes all field values."""
    person = PersonFactory(address_book, u'Tester')
    PostalAddressFactory(
        person, city=u'Dunkelhausen', country=gocept.country.db.Country('CH'))
    # XXX test not yet complete
    assert 0

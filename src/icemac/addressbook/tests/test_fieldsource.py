import zope.i18n
from ..fieldsource import source
from ..fieldsource import tokenize
import icemac.addressbook.interfaces


def interpolate(msgid):
    """Interpolate with the mapping of the message id."""
    return zope.i18n.interpolate(msgid, mapping=msgid.mapping)


def test_fieldsource__Source__getTitle__1(address_book):
    """I uses customized field labels as title."""
    field = icemac.addressbook.interfaces.IPersonName['first_name']
    entity = icemac.addressbook.interfaces.IEntity(
        icemac.addressbook.interfaces.IPerson)
    value = tokenize(entity, field.__name__)

    assert u'person -- first name' == interpolate(
        source.factory.getTitle(value))

    customization = icemac.addressbook.interfaces.IFieldCustomization(
        address_book)
    customization.set_value(field, u'label', u'second name')

    assert u'person -- second name' == interpolate(
        source.factory.getTitle(value))

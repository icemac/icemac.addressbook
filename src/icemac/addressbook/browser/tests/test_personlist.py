from icemac.addressbook.browser.personlist import createFieldColumn
from mock import Mock
import icemac.addressbook.interfaces


def test_personlist__createFieldColumn__1(address_book):
    """I uses customized field labels as title."""
    field = icemac.addressbook.interfaces.IPersonName['first_name']
    entity = icemac.addressbook.interfaces.IEntity(
        icemac.addressbook.interfaces.IPerson)
    column = createFieldColumn(Mock(), entity, field, weight=10)
    assert u'first name' == column.header

    customization = icemac.addressbook.interfaces.IFieldCustomization(
        address_book)
    customization.set_value(field, u'label', u'second name')
    column = createFieldColumn(Mock(), entity, field, weight=10)
    assert u'second name' == column.header

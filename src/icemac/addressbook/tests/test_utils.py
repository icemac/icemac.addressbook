from ..utils import copy_schema_fields
import zope.interface
import zope.schema


def test_utils__copy_schema_fields__1():
    """It copies the schema fields of in interface to another one."""

    class I1(zope.interface.Interface):
        field_1 = zope.schema.TextLine()
        field_2 = zope.schema.TextLine()

    class I2(I1):
        pass

    assert I2['field_1'].interface == I1
    assert I2['field_2'].interface == I1

    copy_schema_fields(I1, I2)

    assert I2['field_1'].interface == I2
    assert I2['field_2'].interface == I2

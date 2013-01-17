import sys
import zope.schema
import zope.schema.fieldproperty


def createFieldProperties(schema, omit=[]):
    """Creates a FieldProperty fields in `schema` on the class it is called on.

    schema ... interface those fields should be added to class
    omit ... list of field names to be omitted in creation

    """
    frame = sys._getframe(1)
    for name in zope.schema.getFieldNamesInOrder(schema):
        if name in omit:
            continue
        frame.f_locals[name] = zope.schema.fieldproperty.FieldProperty(
            schema[name])

import unittest
import zope.interface
import zope.schema


class IDummy(zope.interface.Interface):

    foo = zope.schema.TextLine(title=u'foo')
    bar = zope.schema.Int(title=u'bar')


class CreateFieldPropertiesTests(unittest.TestCase):
    """Testing ..schema.createFieldProperties()."""

    def test_creates_fieldproperties_on_class(self):
        from ..schema import createFieldProperties
        from zope.schema.fieldproperty import FieldProperty

        class Dummy(object):
            createFieldProperties(IDummy)

        self.assertTrue(isinstance(Dummy.foo, FieldProperty))
        self.assertTrue(isinstance(Dummy.bar, FieldProperty))
        self.assertTrue(Dummy.foo._FieldProperty__field is IDummy['foo'])

    def test_fields_in_omit_are_not_created_on_class(self):
        from ..schema import createFieldProperties
        from zope.schema.fieldproperty import FieldProperty

        class Dummy(object):
            createFieldProperties(IDummy, omit=['foo'])

        self.assertFalse(hasattr(Dummy, 'foo'))
        self.assertTrue(hasattr(Dummy, 'bar'))

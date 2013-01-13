# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.testing
import unittest


class SerializableObject(object):

    text = u'asdf'
    number1 = 2411
    number2 = 1234.6789
    bytes = 'foobar'


class TestFieldSerializer(unittest.TestCase):

    def callFUT(self, field_class_name, field_name, serializer_class_name,
                expected_result):
        import zope.schema
        import icemac.addressbook.catalog.serializer

        field = getattr(zope.schema, field_class_name)(title=u'')
        field.__name__ = field_name
        serializer = getattr(icemac.addressbook.catalog.serializer,
                             serializer_class_name)
        result = serializer(field, SerializableObject())
        self.assertTrue(isinstance(result, unicode))
        self.assertEqual(expected_result, result)

    def test_serializer_returns_field_value_of_textline_as_unicode(self):
        self.callFUT('TextLine', 'text', 'FieldSerializer', u'asdf')

    def test_serializer_returns_field_value_of_text_as_unicode(self):
        self.callFUT('Text', 'text', 'FieldSerializer', u'asdf')

    def test_serializer_returns_field_value_of_int_as_unicode(self):
        self.callFUT('Int', 'number1', 'FieldSerializer', u'2411')

    def test_serializer_returns_field_value_of_float_as_unicode(self):
        self.callFUT('Float', 'number2', 'FieldSerializer', u'1234.6789')

    def test_noserializer_returns_empty_unicode(self):
        self.callFUT('Bytes', 'bytes', 'FieldNoSerializer', u'')


class TestObjectSerializer(unittest.TestCase):

    layer = icemac.addressbook.testing.ZODB_LAYER

    def test_serializer_serializes_all_field_values(self):
        import gocept.country.db
        import icemac.addressbook.address

        address = icemac.addressbook.address.PostalAddress()
        address.city = u'Dunkelhausen'
        address.country = gocept.country.db.Country('DE')
        # XXX test not yet complete

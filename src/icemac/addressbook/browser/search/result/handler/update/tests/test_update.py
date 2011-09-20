# -*- coding: utf-8 -*-
# Copyright (c) 2011 Michael Howitz
# See also LICENSE.txt
import decimal
import icemac.addressbook.browser.testing
import icemac.addressbook.testing
import unittest2 as unittest


class TestEmptyNewValue(unittest.TestCase):
    """Testing handler for edge case that user enters empty new value."""

    layer = icemac.addressbook.browser.testing.WSGI_SEARCH_LAYER

    def test_adding_an_empty_new_value_does_not_change_the_updated_value(self):
        from icemac.addressbook.browser.search.result.handler.update.testing \
            import select_persons_with_keyword_for_update
        browser = select_persons_with_keyword_for_update('family')
        browser.getControl('field').displayValue = ['person -- last name']
        browser.getControl('Next').click()
        browser.getControl('new value', index=0).value = ''
        browser.getControl('operation').displayValue = [
            'append new value to existing one']
        browser.getControl('Next').click()
        # The last name column is displayed as a link column it contains the
        # unchanged last name:
        self.assertIn(
            '<td><a href="http://localhost/ab/Person-2">Koch</a></td>',
            browser.contents)


KEYWORD = u'keyword for test'


class TestUserDefinedFields(unittest.TestCase):
    """Testing update of user defined fields."""

    layer = icemac.addressbook.testing.WSGI_ADDRESS_BOOK_FUNCTIONAL_LAYER

    def setUp(self):
        self.ab = self.layer['rootFolder']['ab']

    def create_updateable_person(self, **kw):
        from icemac.addressbook.interfaces import IEntity, IPerson
        keyword = icemac.addressbook.testing.create_keyword(self.ab, KEYWORD)
        data = {'last_name': u'Tester', 'keywords': set([keyword]),
                'return_obj': True}
        data.update(kw)
        return icemac.addressbook.testing.create(
            self.ab, self.ab, IEntity(IPerson).class_name, **data)

    def test_bool_field_can_be_updated(self):
        from icemac.addressbook.interfaces import IEntity, IPerson
        from icemac.addressbook.browser.search.result.handler.update.testing \
            import select_persons_with_keyword_for_update
        field_name = icemac.addressbook.testing.create_field(
            self.ab, IEntity(IPerson).class_name, 'Bool', u'Ever met')
        self.create_updateable_person(**{field_name: False})
        browser = select_persons_with_keyword_for_update(KEYWORD)

        browser.getControl('field').displayValue = ['person -- Ever met']
        browser.getControl('Next').click()
        browser.getControl('yes').click()
        browser.getControl('operation').displayValue = [
            'replace existing value with new one']
        browser.getControl('Next').click()
        # Update sets the value to 'yes':
        self.assertIn('<td>Tester</td><td>yes</td>',
                      browser.contents.replace(' ', '').replace('\n', ''))

    def test_choice_field_can_be_updated(self):
        from icemac.addressbook.interfaces import IEntity, IPostalAddress
        address_class_name = IEntity(IPostalAddress).class_name
        field_name = icemac.addressbook.testing.create_field(
            self.ab, address_class_name, 'Choice', u'distance',
            values=[u'< 50 km', u'>= 50 km'])
        person = self.create_updateable_person()
        icemac.addressbook.testing.create(
            self.ab, person, address_class_name,
            **{field_name: '>= 50 km', 'set_as_default': True})
        from icemac.addressbook.browser.search.result.handler.update.testing \
            import select_persons_with_keyword_for_update
        browser = select_persons_with_keyword_for_update(KEYWORD)

        browser.getControl('field').displayValue = [
            'postal address -- distance']
        browser.getControl('Next').click()
        self.assertEqual(['no value', '< 50 km', '>= 50 km'],
                         browser.getControl('new value').displayOptions)
        browser.getControl('new value').displayValue = ['< 50 km']
        browser.getControl('operation').displayValue = [
            'replace existing value with new one']
        browser.getControl('Next').click()
        # Update sets the value to '< 50 km':
        self.assertIn('<td>Tester</td><td><50km</td>',
                      browser.contents.replace(' ', '').replace('\n', ''))

    def test_keywords_field_can_be_updated(self):
        from icemac.addressbook.interfaces import IEntity, IPerson
        person = self.create_updateable_person()
        icemac.addressbook.testing.create_keyword(self.ab, u'second kw')
        from icemac.addressbook.browser.search.result.handler.update.testing \
            import select_persons_with_keyword_for_update
        browser = select_persons_with_keyword_for_update(KEYWORD)

        browser.handleErrors = False
        browser.getControl('field').displayValue = ['person -- keywords']
        browser.getControl('Next').click()
        self.assertEqual([KEYWORD, 'second kw'],
                         browser.getControl('new value').displayOptions)
        browser.getControl('new value').displayValue = ['second kw']
        browser.getControl('operation').displayValue = [
            'append selected keywords to existing ones']
        browser.getControl('Next').click()
        self.assertIn('<td>Tester</td><td>keywordfortest,secondkw</td>',
                      browser.contents.replace(' ', '').replace('\n', ''))

    def _assert_number_field_can_be_updated(self, field_type, field_class):
        from icemac.addressbook.interfaces import IEntity, IPostalAddress
        address_class_name = IEntity(IPostalAddress).class_name
        field_name = icemac.addressbook.testing.create_field(
            self.ab, address_class_name, field_type, u'distance')
        person = self.create_updateable_person()
        icemac.addressbook.testing.create(
            self.ab, person, address_class_name,
            **{field_name: field_class(50), 'set_as_default': True})
        from icemac.addressbook.browser.search.result.handler.update.testing \
            import select_persons_with_keyword_for_update
        browser = select_persons_with_keyword_for_update(KEYWORD)

        browser.getControl('field').displayValue = [
            'postal address -- distance']
        browser.getControl('Next').click()
        self.assertEqual('', browser.getControl('new value', index=0).value)
        browser.getControl('new value', index=0).value = '5'
        browser.getControl('operation').displayValue = ['add']
        browser.getControl('Next').click()
        # Update sets the value to 55:
        self.assertIn('<td>Tester</td><td>55</td>',
                      browser.contents.replace(' ', '').replace('\n', ''))

    def test_int_field_can_be_updated(self):
        self._assert_number_field_can_be_updated('Int', int)

    def test_decimal_field_can_be_updated(self):
        self._assert_number_field_can_be_updated('Decimal', decimal.Decimal)

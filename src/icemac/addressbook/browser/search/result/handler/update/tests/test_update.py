# -*- coding: utf-8 -*-
import decimal
import icemac.addressbook.browser.testing
import icemac.addressbook.testing
import unittest


class TestEmptyNewValue(unittest.TestCase):
    """Testing handler for edge case that user enters empty new value."""

    layer = icemac.addressbook.browser.testing.WSGI_SEARCH_LAYER

    def test_adding_an_empty_new_value_does_not_change_the_updated_value(self):
        from icemac.addressbook.browser.search.result.handler.update.testing \
            import select_persons_with_keyword_for_update
        browser = select_persons_with_keyword_for_update(self.layer, 'family')
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

    layer = icemac.addressbook.testing.TEST_BROWSER_LAYER

    def setUp(self):
        self.ab = self.layer['addressbook']

    def create_updateable_person(self, **kw):
        from icemac.addressbook.interfaces import IEntity, IPerson
        keywords = set(
            icemac.addressbook.testing.create_keyword(self.ab, keyword)
            for keyword in kw.pop('keywords', [KEYWORD]))
        data = {'last_name': u'Tester', 'keywords': keywords,
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
        browser = select_persons_with_keyword_for_update(self.layer, KEYWORD)

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
        browser = select_persons_with_keyword_for_update(self.layer, KEYWORD)

        browser.getControl('field').displayValue = [
            'postal address -- distance']
        browser.getControl('Next').click()
        self.assertEqual(['No value', '< 50 km', '>= 50 km'],
                         browser.getControl('new value').displayOptions)
        browser.getControl('new value').displayValue = ['< 50 km']
        browser.getControl('operation').displayValue = [
            'replace existing value with new one']
        browser.getControl('Next').click()
        # Update sets the value to '< 50 km':
        self.assertIn('<td>Tester</td><td><50km</td>',
                      browser.contents.replace(' ', '').replace('\n', ''))

    def test_keywords_field_can_be_updated(self):
        from icemac.addressbook.browser.search.result.handler.update.testing \
            import select_persons_with_keyword_for_update
        self.create_updateable_person(keywords=[KEYWORD, u'second kw'])
        browser = select_persons_with_keyword_for_update(
            self.layer, u'second kw')

        browser.getControl('field').displayValue = ['person -- keywords']
        browser.getControl('Next').click()
        self.assertEqual([KEYWORD, 'second kw'],
                         browser.getControl('new value').displayOptions)
        browser.getControl('new value').displayValue = ['second kw']
        browser.getControl('operation').displayValue = [
            'remove selected keywords from existing ones']
        browser.getControl('Next').click()
        self.assertIn('<td>Tester</td><td>keywordfortest</td>',
                      browser.contents.replace(' ', '').replace('\n', ''))
        browser.getControl('Complete').click()
        # After removing the keyword from the person no person can be found:
        from icemac.addressbook.browser.testing import (
            search_for_persons_with_keyword_search_using_browser)
        browser = search_for_persons_with_keyword_search_using_browser(
            self.layer, 'second kw')
        self.assertIn('No person found.', browser.contents)

    def _create_user_defined_field(self, field_type, field_class):
        """Create a user defined field."""
        from icemac.addressbook.interfaces import IEntity, IPostalAddress
        address_class_name = IEntity(IPostalAddress).class_name
        field_name = icemac.addressbook.testing.create_field(
            self.ab, address_class_name, field_type, u'distance')
        person = self.create_updateable_person()
        icemac.addressbook.testing.create(
            self.ab, person, address_class_name,
            **{field_name: field_class(50), 'set_as_default': True})

    def _update_field_value(self, field_name, operator, value):
        """Update a number field."""
        from icemac.addressbook.browser.search.result.handler.update.testing \
            import select_persons_with_keyword_for_update
        browser = select_persons_with_keyword_for_update(self.layer, KEYWORD)

        browser.getControl('field').displayValue = [field_name]
        browser.getControl('Next').click()
        self.assertEqual('', browser.getControl('new value', index=0).value)
        browser.getControl('new value', index=0).value = value
        browser.getControl('operation').displayValue = [operator]
        browser.getControl('Next').click()
        return browser

    def _assert_number_field_can_be_updated(
            self, field_type, field_class, operator='add', value='5'):
        """Assert that a number field can be updated as expected."""
        self._create_user_defined_field(field_type, field_class)
        browser = self._update_field_value(
            'postal address -- distance', operator, value)
        # Update sets the value to 55:
        self.assertIn('<td>Tester</td><td>55</td>',
                      browser.contents.replace(' ', '').replace('\n', ''))

    def test_int_field_can_be_updated(self):
        self._assert_number_field_can_be_updated('Int', int)

    def test_decimal_field_can_be_updated(self):
        self._assert_number_field_can_be_updated('Decimal', decimal.Decimal)

    def test_validation_errors_show_up_in_result_table(self):
        from icemac.addressbook.interfaces import IEntity, IEMailAddress
        person = self.create_updateable_person()
        icemac.addressbook.testing.create(
            self.ab, person,
            IEntity(IEMailAddress).class_name, set_as_default=True)
        browser = self._update_field_value(
            'e-mail address -- e-mail address', 'append', 'foo')
        self.assertIn(
            '<td>Tester</td><td></td><td>fooisnotavalide-mailaddress.</td>',
            browser.contents.replace(' ', '').replace('\n', ''))
        # Complete button is not shown:
        self.assertEqual(
            ['form.buttons.back'],
            icemac.addressbook.testing.get_submit_control_names(browser))

    def test_division_by_zero_is_handled_like_a_validation_error(self):
        self._create_user_defined_field('Int', int)
        browser = self._update_field_value(
            'postal address -- distance', 'div', '0')
        self.assertIn('<td>Tester</td><td>50</td><td>Divisionbyzero</td>',
                      browser.contents.replace(' ', '').replace('\n', ''))
        # Complete button is not shown:
        self.assertEqual(
            ['form.buttons.back'],
            icemac.addressbook.testing.get_submit_control_names(browser))

    def test_datatype_of_field_for_change_can_be_changed(self):
        self.create_updateable_person()
        browser = self._update_field_value(
            'person -- first name', 'append', 'foo')
        browser.getControl('Back').click()
        browser.getControl('Back').click()
        browser.getControl('field').displayValue = ['person -- birth date']
        browser.getControl('Next').click()
        # Another field is used to avoid conflicts on data types:
        self.assertEqual('', browser.getControl('new value').value)

    def test_not_hitting_complete_button_does_not_persist_any_changes(self):
        self.create_updateable_person()
        browser = self._update_field_value(
            'person -- last name', 'append', 'foo')
        browser.getLink('Person list').click()
        # The last name of person 'Tester' is unchanged:
        self.assertIn('<a href="http://localhost/ab/Person">Tester</a>',
                      browser.contents)

    def test_if_user_selects_a_step_with_data_missing_he_gets_redirected_back(
            self):
        self.create_updateable_person()
        from icemac.addressbook.browser.search.result.handler.update.testing \
            import select_persons_with_keyword_for_update
        browser = select_persons_with_keyword_for_update(self.layer, KEYWORD)
        self.assertEqual('http://localhost/ab/@@multi-update', browser.url)
        browser.getLink('New value').click()
        # 'chooseField' is the first step, so we get redirected there
        self.assertEqual(
            'http://localhost/ab/multi-update/chooseField', browser.url)
        browser.getLink('Check result').click()
        self.assertEqual(
            'http://localhost/ab/multi-update/chooseField', browser.url)
        browser.getControl('field').displayValue = ['person -- first name']
        browser.getControl('Next').click()

        self.assertEqual(
            'http://localhost/ab/multi-update/enterValue', browser.url)
        browser.getLink('Choose field').click()
        self.assertEqual(
            'http://localhost/ab/multi-update/chooseField', browser.url)
        browser.getLink('Check result').click()
        # After selecting the field 'enterValue' is complete, as the only
        # required field has a default value
        self.assertEqual(
            'http://localhost/ab/multi-update/checkResult', browser.url)
        # There is no 'complete' button as the user did not enter data in step
        # 'enterValue':
        self.assertEqual(
            ['form.buttons.back'],
            icemac.addressbook.testing.get_submit_control_names(browser))

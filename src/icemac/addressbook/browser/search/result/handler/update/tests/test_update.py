# -*- coding: utf-8 -*-
# Copyright (c) 2011 Michael Howitz
# See also LICENSE.txt
import icemac.addressbook.browser.testing
import unittest2 as unittest


class TestEmptyNewValue(unittest.TestCase):
    """Testing handler for edge case that user enters empty new value."""

    layer = icemac.addressbook.browser.testing.WSGI_SEARCH_LAYER

    def test_adding_an_empty_new_value_does_not_change_the_updated_value(self):
        from icemac.addressbook.browser.search.result.handler.update.testing \
            import select_persons_with_keyword_church_for_update
        browser = select_persons_with_keyword_church_for_update()
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


class TestUserDefinedFields(unittest.TestCase):
    """Testing update of user defined fields."""

    layer = icemac.addressbook.browser.testing.WSGI_SEARCH_LAYER

    def test_bool_field_can_be_updated(self):
        from icemac.addressbook.testing import create_field
        from icemac.addressbook.interfaces import IEntity, IPerson
        from icemac.addressbook.testing import Browser
        create_field(
            self.layer['rootFolder']['ab'], IEntity(IPerson).class_name,
            'Bool', u'Ever met?')
        browser = Browser()
        browser.login('mgr')
        browser.open('http://localhost/ab')
        browser.getLink('Koch').click()
        # We set the value for the person under test to 'no':
        browser.getControl('no', index=0).click()
        browser.getControl('Apply').click()
        self.assertEqual(
            ['Data successfully updated.'], browser.get_messages())
        from icemac.addressbook.browser.search.result.handler.update.testing \
            import select_persons_with_keyword_church_for_update
        browser = select_persons_with_keyword_church_for_update(browser)

        browser.getControl('field').displayValue = ['person -- Ever met?']
        browser.getControl('Next').click()
        browser.getControl('yes').click()
        browser.getControl('operation').displayValue = [
            'replace existing value with new one']
        browser.getControl('Next').click()
        # Updated sets the value to 'yes':
        self.assertIn('<td>Koch</td><td>yes</td>',
                      browser.contents.replace(' ', '').replace('\n', ''))

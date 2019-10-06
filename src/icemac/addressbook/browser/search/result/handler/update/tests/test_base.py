# -*- coding: utf-8 -*-
from ..base import update_persons, clean_update_data_session
from icemac.addressbook.person import Person, person_entity
import mock
import zope.i18n
import zope.publisher.browser


def test_base__update_persons__1(zcmlS):
    """It updates only the specified field."""
    person1 = Person()
    person1.notes = u'p1'
    person2 = Person()
    person2.notes = u'p2'
    update_persons((person1, person2), person_entity,
                   person_entity.getRawField('notes'), 'append', u'bar')
    assert 'p1bar' == person1.notes
    assert 'p2bar' == person2.notes
    # no other attributes are in vars as they are not changed (only the
    # private container attributes are additionally here).
    assert set(['notes', '_BTreeContainer__len', '_SampleContainer__data',
                '__annotations__']) == set(vars(person1).keys())


def test_base__update_persons__2(zcmlS):
    """It returns a ZeroDivision message if dividing by zero."""
    person1 = Person()
    person1.__name__ = 'person1'
    call = ('icemac.addressbook.browser.search.result.handler.update.'
            'operators.NoneAppend.__call__')
    with mock.patch(call, side_effect=ZeroDivisionError):
        result = update_persons(
            [person1], person_entity,
            person_entity.getRawField('notes'), 'append', u'bar')
    assert ({'person1': u'Division by zero'}, {'person1': None}) == result


def test_base__update_persons__3(zcmlS):
    """It returns an Exception if another exception occurred."""
    call = ('icemac.addressbook.browser.search.result.handler.update.'
            'operators.NoneAppend.__call__')
    person1 = Person()
    person1.__name__ = 'person1'
    with mock.patch(call, side_effect=IOError('file not found')):
        result = update_persons(
            [person1], person_entity,
            person_entity.getRawField('notes'), 'append', u'bar')
    errors = {key: zope.i18n.translate(val)
              for key, val in result[0].items()}
    assert (
        {'person1': u'Unexpected error occurred: IOError: file not found'} ==
        errors)


def test_base__clean_update_data_session__1(address_book):
    """It does not break if `UPDATE_SESSION_KEY` is not in the session."""
    request = zope.publisher.browser.TestRequest()
    clean_update_data_session(request)

# -*- coding: utf-8 -*-
from ..base import update_persons
from icemac.addressbook.person import Person, person_entity
import mock
import zope.i18n


def test_base__update_persons__1(zcmlS):
    """..base.update_persons() updates only the specified field."""
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
    """update_persons() returns a ZeroDivision message if dividing by zero."""
    person1 = Person()
    person1.__name__ = 'person1'
    call = ('icemac.addressbook.browser.search.result.handler.update.'
            'operators.NoneAppend.__call__')
    with mock.patch(call, side_effect=ZeroDivisionError):
        result = update_persons(
            [person1], person_entity,
            person_entity.getRawField('notes'), 'append', u'bar')
    assert {'person1': u'Division by zero'} == result


def test_base__update_persons__3(zcmlS):
    """update_persons() returns an Exception if another exception occurred."""
    call = ('icemac.addressbook.browser.search.result.handler.update.'
            'operators.NoneAppend.__call__')
    person1 = Person()
    person1.__name__ = 'person1'
    with mock.patch(call, side_effect=IOError('file not found')):
        result = update_persons(
            [person1], person_entity,
            person_entity.getRawField('notes'), 'append', u'bar')
    assert (
        {'person1': u'Unexpected error occurred: IOError: file not found'} ==
        {key: zope.i18n.translate(val) for key, val in result.items()})

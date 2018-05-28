# -*- coding: utf-8 -*-
from icemac.addressbook.entities import Field
from icemac.addressbook.interfaces import IField
from zope.interface.exceptions import Invalid
from zope.schema import getValidationErrors
import pytest


@pytest.fixture('function')
def field():
    """Get a preconfigured field object."""
    field = Field()
    field.title = u'my field'
    field.order = 1.5
    return field


def test_interfaces__IField__1(field):
    """It does not raise `Invalid` if the field type is not 'choice'."""
    field.type = u'Text'
    errors = getValidationErrors(IField, field)
    assert [] == errors


def test_interfaces__IField__2(field):
    """Using the `choice` type requires values to be added."""
    field.type = u'Choice'
    errors = getValidationErrors(IField, field)
    assert 1 == len(errors)
    assert errors[0][0] is None
    assert isinstance(errors[0][1], Invalid)
    assert ((u'type "choice" requires at least one field value.',) ==
            errors[0][1].args)


def test_interfaces__IField__3(field):
    """It does not raise `Invalid` if there are values for a choice field."""
    field.type = u'Choice'
    field.values = [u'sure', u'not really']
    errors = getValidationErrors(IField, field)
    assert [] == errors

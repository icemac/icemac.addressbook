# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

import doctest
import icemac.addressbook.namechooser.namechooser
import zope.annotation.attribute
import zope.testing.cleanup
import zope.testrunner.layer


class NameChooserLayer(zope.testrunner.layer.UnitTests):
    """Layer for name chooser tests."""

    @classmethod
    def setUp(cls):
        zope.component.provideAdapter(
            zope.annotation.attribute.AttributeAnnotations)
        zope.component.provideAdapter(
            icemac.addressbook.namechooser.namechooser.name_suffix)

    @classmethod
    def tearDown(cls):
        zope.testing.cleanup.tearDown()


def test_suite():
    suite = doctest.DocFileSuite('namechooser.txt')
    suite.layer = NameChooserLayer
    return suite


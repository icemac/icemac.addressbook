# -*- coding: utf-8 -*-
# Copyright (c) 2009-2014 Michael Howitz
# See also LICENSE.txt

import doctest
import icemac.addressbook.namechooser.namechooser
import plone.testing
import plone.testing.zca
import zope.annotation.attribute
import zope.testing.cleanup


class NameChooserLayer(plone.testing.Layer):
    """Layer for name chooser tests."""
    defaultBases = [plone.testing.zca.LAYER_CLEANUP]

    def setUp(self):
        zope.component.provideAdapter(
            zope.annotation.attribute.AttributeAnnotations)
        zope.component.provideAdapter(
            icemac.addressbook.namechooser.namechooser.name_suffix)

    def tearDown(self):
        zope.testing.cleanup.tearDown()

NAME_CHOOSER_LAYER = NameChooserLayer()


def test_suite():
    suite = doctest.DocFileSuite('namechooser.txt')
    suite.layer = NAME_CHOOSER_LAYER
    return suite

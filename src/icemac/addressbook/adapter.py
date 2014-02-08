# -*- coding: latin-1 -*-
# Copyright (c) 2008-2014 Michael Howitz
# See also LICENSE.txt
# $Id$

import zope.interface
import zope.schema.interfaces
import zope.site.hooks

import icemac.addressbook.interfaces
import icemac.addressbook.principals.interfaces


@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def gocept_country_title(obj):
    """Title for objects from gocept.country."""
    return obj.name


@zope.component.adapter(zope.schema.interfaces.IChoice,
                        zope.interface.Interface)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def title_for_choice_value(field, value):
    "Get the title for a value of a field which is a Choice."
    factory = field.source.factory
    return factory.getTitle(value)


@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def obj_dot_title(obj):
    "ITitle adapter for objects those title is stored on the title attribute."
    return obj.title


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def default_title(obj):
    "Default title adapter which returns str represantation of obj."
    if isinstance(obj, basestring):
        return obj
    return str(obj)


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(icemac.addressbook.principals.interfaces.IRoot)
def principal_root(principal):
    return zope.site.hooks.getSite()

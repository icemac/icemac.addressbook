# -*- coding: latin-1 -*-
# Copyright (c) 2008-2014 Michael Howitz
# See also LICENSE.txt
# $Id$

import zope.interface
import zope.schema.interfaces
import zope.component.hooks

import icemac.addressbook.interfaces
import icemac.addressbook.principals.interfaces


@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def gocept_country_title(obj):
    """Title for objects from gocept.country."""
    return obj.name


@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def obj_dot_title(obj):
    """Title for an `obj` where the title is stored on `title` attribute."""
    return obj.title


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def default_title(obj):
    """Default title adapter which returns `str` representation of `obj`."""
    if isinstance(obj, basestring):
        return obj
    return str(obj)


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(icemac.addressbook.principals.interfaces.IRoot)
def principal_root(principal):
    """Return the site root."""
    return zope.component.hooks.getSite()

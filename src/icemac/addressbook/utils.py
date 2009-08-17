# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

import zope.container.interfaces
import zope.event
import zope.lifecycleevent
import zope.site.hooks


def set_site(func):
    "Decorator which does the set-site-dance."
    def decorated(site, *args, **kw):
        old_site = zope.site.hooks.getSite()
        try:
            zope.site.hooks.setSite(site)
            return func(*args, **kw)
        finally:
            zope.site.hooks.setSite(old_site)
    return decorated


def create_obj(class_, *args, **kw):
    """Create an object of class and fire created event."""
    obj = class_(*args)
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
    for attrib, value in kw.items():
        setattr(obj, attrib, value)
    return obj


create_obj_with_set_site = set_site(create_obj)


def add(parent, obj):
    nc = zope.container.interfaces.INameChooser(parent)
    name = nc.chooseName('', obj)
    parent[name] = obj
    return name


def create_and_add(parent, class_, *args, **kw):
    obj = create_obj(class_, *args, **kw)
    return add(parent, obj)


create_and_add_with_set_site = set_site(create_and_add)


def iter_by_interface(container, interface):
    "Iterate a container and return only objects providing the specified iface."
    for obj in container.values():
        if interface.providedBy(obj):
            yield obj


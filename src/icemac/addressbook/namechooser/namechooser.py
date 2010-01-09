# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

import BTrees.Length
import icemac.addressbook.namechooser.interfaces
import persistent
import zope.component
import zope.interface


class NameSuffix(persistent.Persistent):
    "Storage for name suffix."

    zope.interface.implements(
        icemac.addressbook.namechooser.interfaces.INameSuffix)
    zope.component.adapts(
        icemac.addressbook.namechooser.interfaces.IDontReuseNames)

    def __init__(self):
        self._suffix = BTrees.Length.Length(0)

    def __iadd__(self, value):
        self._suffix.change(value)
        return self

    def __unicode__(self):
        return unicode(self._suffix.value)


name_suffix = zope.annotation.factory(
    NameSuffix, key='icemac.namechooser.DontReuseNames.NameSuffix')


class DontReuseNames(zope.container.contained.NameChooser):

    zope.component.adapts(
        icemac.addressbook.namechooser.interfaces.IDontReuseNames)

    def chooseName(self, name, object):
        container = self.context

        # remove characters that checkName does not allow
        name = unicode(name.replace('/', '-').lstrip('+@'))

        if not name:
            name = unicode(object.__class__.__name__)

        dot = name.rfind('.')
        if dot >= 0:
            extension = name[dot:]
            name = name[:dot]
        else:
            extension = ''

        name_suffix = icemac.addressbook.namechooser.interfaces.INameSuffix(
            container)
        while True:
            name_suffix += 1
            n = name + u'-' + unicode(name_suffix) + extension
            if n not in container:
                break

        # Make sure the name is valid.  We may have started with something bad.
        self.checkName(n, object)

        return n


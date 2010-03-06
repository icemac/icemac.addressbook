# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import MessageFactory as _
import ZODB.blob
import classproperty
import icemac.addressbook.entities
import icemac.addressbook.file.interfaces
import icemac.addressbook.interfaces
import persistent
import zope.container.contained
import zope.interface
import icemac.addressbook.file.file

class Image(icemac.addressbook.file.file.File):
    "An image."

    zope.interface.implements(icemac.addressbook.file.interfaces.IImage)


image_entity = icemac.addressbook.entities.create_entity(
    _(u'image'), icemac.addressbook.file.interfaces.IImage, Image)

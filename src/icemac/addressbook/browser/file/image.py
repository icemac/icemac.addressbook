# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.browser.base
import icemac.addressbook.file.file
import icemac.addressbook.file.interfaces
import os.path
import z3c.form.field
import z3c.form.widget
import zope.component
import zope.mimetype.interfaces
import zope.security.proxy
import icemac.addressbook.file.image
import icemac.addressbook.browser.file.file
import z3c.form.widget

def get_file_entity():
    return zope.component.getUtility(
        icemac.addressbook.interfaces.IEntity,
        name='icemac.addressbook.file.image.Image')


ImageLabel = z3c.form.widget.StaticWidgetAttribute(
    _(u'image'),
    field=icemac.addressbook.file.interfaces.IImage['data'])


class Add(icemac.addressbook.browser.file.file.Add):
    "Add an image."

    label = _(u'Add image')
    class_ = icemac.addressbook.file.image.Image
    next_url = 'parent'

    @property
    def fields(self):
        return z3c.form.field.Fields(
            *get_file_entity().getFieldValuesInOrder()).omit(
            'name', 'mimeType', 'size')


class DeleteImageForm(icemac.addressbook.browser.base.BaseDeleteForm):
    "Are you sure question for deleting an image."

    next_url = 'parent'
    label = _(u'Do you really want to delete this image?')
    interface = icemac.addressbook.file.interfaces.IImage
    field_names = ('name', )

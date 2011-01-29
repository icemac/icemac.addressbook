# -*- coding: utf-8 -*-
# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id$

import zope.traversing.api

import icemac.addressbook.address
import icemac.addressbook.browser.base
import icemac.addressbook.interfaces

from icemac.addressbook.i18n import MessageFactory as _


class DefaultsDeleteForm(icemac.addressbook.browser.base.BaseDeleteForm):

    next_url = 'parent'

    def _do_delete(self):
        parent = zope.traversing.api.getParent(self.context)
        entity = icemac.addressbook.interfaces.IEntity(self.context)
        default_attr = entity.tagged_values.get('default_attrib', None)
        if default_attr is not None:
            default_obj = getattr(parent, default_attr)
            if self.context == default_obj:
                replacement_obj = icemac.addressbook.utils.create_obj(
                    entity.getClass())
                icemac.addressbook.utils.add(parent, replacement_obj)
                setattr(parent, default_attr, replacement_obj)
        super(DefaultsDeleteForm, self)._do_delete()


class AddPhoneNumberForm(icemac.addressbook.browser.base.BaseAddForm):

    label = _(u'Add phone number')
    interface = icemac.addressbook.interfaces.IPhoneNumber
    class_ = icemac.addressbook.address.PhoneNumber
    next_url = 'parent'


class DeletePhoneNumberForm(DefaultsDeleteForm):

    label = _(u'Do you really want to delete this phone number?')
    interface = icemac.addressbook.interfaces.IPhoneNumber


class AddPostalAddressForm(icemac.addressbook.browser.base.BaseAddForm):

    label = _(u'Add postal address')
    interface = icemac.addressbook.interfaces.IPostalAddress
    class_ = icemac.addressbook.address.PostalAddress
    next_url = 'parent'


class DeletePostalAddressForm(DefaultsDeleteForm):

    label = _(u'Do you really want to delete this postal address?')
    interface = icemac.addressbook.interfaces.IPostalAddress


class AddEMailAddressForm(icemac.addressbook.browser.base.BaseAddForm):

    label = _(u'Add e-mail address')
    interface = icemac.addressbook.interfaces.IEMailAddress
    class_ = icemac.addressbook.address.EMailAddress
    next_url = 'parent'


class DeleteEMailAddressForm(DefaultsDeleteForm):

    label = _(u'Do you really want to delete this e-mail address?')
    interface = icemac.addressbook.interfaces.IEMailAddress


class AddHomePageAddressForm(icemac.addressbook.browser.base.BaseAddForm):

    label = _(u'Add home page address')
    interface = icemac.addressbook.interfaces.IHomePageAddress
    class_ = icemac.addressbook.address.HomePageAddress
    next_url = 'parent'


class DeleteHomePageAddressForm(DefaultsDeleteForm):

    label = _(u'Do you really want to delete this home page address?')
    interface = icemac.addressbook.interfaces.IHomePageAddress

# -*- coding: utf-8 -*-
from icemac.addressbook.i18n import _
import icemac.addressbook.address
import icemac.addressbook.browser.base
import icemac.addressbook.interfaces
import zope.traversing.api


class DefaultsDeleteForm(icemac.addressbook.browser.base.BaseDeleteForm):

    next_url_after_cancel = 'parent'

    def _do_delete(self):
        parent = zope.traversing.api.getParent(self.context)
        entity = icemac.addressbook.interfaces.IEntity(self.context)
        default_attr = entity.tagged_values.get('default_attrib', None)
        assert default_attr is not None
        default_obj = getattr(parent, default_attr)
        if self.context == default_obj:
            replacement_obj = icemac.addressbook.utils.create_obj(
                entity.getClass())
            icemac.addressbook.utils.add(parent, replacement_obj)
            setattr(parent, default_attr, replacement_obj)
        return super(DefaultsDeleteForm, self)._do_delete()


class AddPhoneNumberForm(icemac.addressbook.browser.base.BaseAddForm):

    title = _(u'Add phone number')
    interface = icemac.addressbook.interfaces.IPhoneNumber
    class_ = icemac.addressbook.address.PhoneNumber
    next_url = 'parent'


class DeletePhoneNumberForm(DefaultsDeleteForm):

    title = _('Delete phone number')
    label = _(u'Do you really want to delete this phone number?')
    interface = icemac.addressbook.interfaces.IPhoneNumber


class AddPostalAddressForm(icemac.addressbook.browser.base.BaseAddForm):

    title = _(u'Add postal address')
    interface = icemac.addressbook.interfaces.IPostalAddress
    class_ = icemac.addressbook.address.PostalAddress
    next_url = 'parent'


class DeletePostalAddressForm(DefaultsDeleteForm):

    title = _('Delete postal address')
    label = _(u'Do you really want to delete this postal address?')
    interface = icemac.addressbook.interfaces.IPostalAddress


class AddEMailAddressForm(icemac.addressbook.browser.base.BaseAddForm):

    title = _(u'Add e-mail address')
    interface = icemac.addressbook.interfaces.IEMailAddress
    class_ = icemac.addressbook.address.EMailAddress
    next_url = 'parent'


class DeleteEMailAddressForm(DefaultsDeleteForm):

    title = _('Delete e-mail address')
    label = _(u'Do you really want to delete this e-mail address?')
    interface = icemac.addressbook.interfaces.IEMailAddress


class AddHomePageAddressForm(icemac.addressbook.browser.base.BaseAddForm):

    title = _(u'Add home page address')
    interface = icemac.addressbook.interfaces.IHomePageAddress
    class_ = icemac.addressbook.address.HomePageAddress
    next_url = 'parent'


class DeleteHomePageAddressForm(DefaultsDeleteForm):

    title = _('Delete home page address')
    label = _(u'Do you really want to delete this home page address?')
    interface = icemac.addressbook.interfaces.IHomePageAddress

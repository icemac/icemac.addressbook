# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

import icemac.addressbook.interfaces
import icemac.addressbook.browser.base
from icemac.addressbook.i18n import MessageFactory as _


class EditForm(icemac.addressbook.browser.base.BaseEditFormWithCancel):

    label = _(u'Edit address book data')
    interface = icemac.addressbook.interfaces.IAddressBook
    next_url = 'object'
    next_view = '@@edit.html'

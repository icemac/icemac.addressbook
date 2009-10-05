# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.interfaces
import zope.interface


class Entities(object):
    "Entities in the address book universe."

    zope.interface.implements(icemac.addressbook.interfaces.IEntities)

    def getPrefixes(self):
        return['address_book',
               'person',
               'postal_address',
               'phone_number',
               'email_address',
               'home_page_address',
               'file',
               'keyword',
               'principal',]

    def getTitle(self, something):
        pass

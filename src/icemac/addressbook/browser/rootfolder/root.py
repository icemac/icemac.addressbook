# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

import z3c.pagelet.browser
import icemac.addressbook.interfaces

from icemac.addressbook.i18n import MessageFactory as _


class FrontPage(z3c.pagelet.browser.BrowserPagelet):
    """Pagelet for the front page."""

    def getAddressBooks(self):
        return [value
                for value in self.context.values()
                if icemac.addressbook.interfaces.IAddressBook.providedBy(value)
                ]

    def countEntries(self, address_book):
        count = len(address_book)
        if count == 1: # XXX use i18n instead!
            entries = _(u'entry')
        else:
            entries = _(u'entries')
        return "%s %s" % (count, entries)

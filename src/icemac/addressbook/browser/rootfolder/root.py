# -*- coding: latin-1 -*-
# Copyright (c) 2008-2013 Michael Howitz
# See also LICENSE.txt
import icemac.addressbook.interfaces
import z3c.pagelet.browser
import zope.size.interfaces
import zope.traversing.browser.absoluteurl
import zope.interface
import icemac.addressbook.browser.interfaces


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class FrontPage(z3c.pagelet.browser.BrowserPagelet):
    """Pagelet for the front page."""

    def getAddressBooks(self):
        result = []
        for ab in self.context.values():
            if not icemac.addressbook.interfaces.IAddressBook.providedBy(ab):
                # only show address books
                continue
            url = zope.traversing.browser.absoluteurl.absoluteURL(
                ab, self.request)
            result.append(dict(
                title=ab.title,
                url=url,
                delete_url=url + '/@@delete_address_book.html',
                count=zope.size.interfaces.ISized(ab).sizeForDisplay()))
        return result

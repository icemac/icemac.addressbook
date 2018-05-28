from icemac.addressbook.i18n import _
import icemac.addressbook.browser.base
import icemac.addressbook.browser.interfaces
import icemac.addressbook.interfaces
import z3c.pagelet.browser
import zope.interface
import zope.size.interfaces


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class FrontPage(z3c.pagelet.browser.BrowserPagelet,
                icemac.addressbook.browser.base.BaseView):
    """Pagelet for the front page."""

    title = _('Address books')

    def getAddressBooks(self):
        result = []
        for ab in self.context.values():
            if not icemac.addressbook.interfaces.IAddressBook.providedBy(ab):
                # only show address books
                continue
            result.append(dict(
                title=ab.title,
                url=self.url(ab),
                delete_url=self.url(ab, 'delete-address_book.html'),
                count=zope.size.interfaces.ISized(ab).sizeForDisplay()))
        return result

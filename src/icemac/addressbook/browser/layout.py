from icemac.addressbook.interfaces import IAddressBook
import zope.contentprovider.provider


class AddressBookTitle(zope.contentprovider.provider.ContentProviderBase):
    """Content provider for the addressbook title string."""

    default_title = u'icemac.addressbook'

    def render(self):
        address_book = IAddressBook(self.context)
        if not IAddressBook.providedBy(address_book):
            return self.default_title
        return address_book.title or self.default_title

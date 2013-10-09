import icemac.addressbook.interfaces


class RootFavIconURL(object):
    """URL to the FavIcon outside an address book."""

    def __call__(self):
        return '/++resource++img/favicon-red.png'


class AddressBookFavIconURL(object):
    """URL to the FavIcon selected in the address book."""

    def __call__(self):
        address_book = icemac.addressbook.interfaces.IAddressBook(self.context)
        return address_book.favicon


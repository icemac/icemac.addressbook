import icemac.addressbook.interfaces
import zope.interface


class RootFavIconURL(object):
    """URL to the FavIcon outside an address book."""

    def __call__(self):
        return icemac.addressbook.interfaces.DEFAULT_FAVICON


class AddressBookFavIconURL(object):
    """URL to the FavIcon selected in the address book."""

    def __call__(self):
        address_book = icemac.addressbook.interfaces.IAddressBook(self.context)
        return address_book.favicon


@zope.interface.implementer(icemac.addressbook.interfaces.IFaviconData)
class FavIconData(object):
    """Data of a FavIcon."""

    def __init__(self, path, preview_path):
        self.path = path
        self.preview_path = preview_path

    def __call__(self, *args):
        return self


red = FavIconData('/++resource++img/favicon-red.ico',
                  '/++resource++img/favicon-red-preview.png')
green = FavIconData('/++resource++img/favicon-green.ico',
                    '/++resource++img/favicon-green-preview.png')
black = FavIconData('/++resource++img/favicon-black.ico',
                    '/++resource++img/favicon-black-preview.png')

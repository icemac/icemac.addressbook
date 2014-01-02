import icemac.addressbook.browser.base
import icemac.addressbook.browser.interfaces
import icemac.addressbook.interfaces
import zope.interface


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class Base(icemac.addressbook.browser.base.BaseView):
    """Base for search result handlers."""

    @property
    def persons(self):
        addressbook = icemac.addressbook.interfaces.IAddressBook(None)
        return [addressbook[id] for id in self.session['person_ids']]

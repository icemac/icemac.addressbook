import icemac.addressbook.browser.base
import icemac.addressbook.browser.interfaces
import icemac.addressbook.interfaces
import zope.interface


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class Base(object):
    """Base for search result handlers."""

    @property
    def persons(self):
        addressbook = icemac.addressbook.interfaces.IAddressBook(None)
        session = icemac.addressbook.browser.base.get_session(self.request)
        return [addressbook[id] for id in session['person_ids']]

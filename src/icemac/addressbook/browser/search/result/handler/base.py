import icemac.addressbook.browser.base
import icemac.addressbook.interfaces


class Base(object):
    """Base for search result handlers."""

    @property
    def persons(self):
        addressbook = icemac.addressbook.interfaces.IAddressBook(None)
        session = icemac.addressbook.browser.base.get_session(self.request)
        return [addressbook[id] for id in session['person_ids']]

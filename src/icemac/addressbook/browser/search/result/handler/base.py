import icemac.addressbook.browser.base
import zope.component.hooks


class Base(object):
    """Base for search result handlers."""

    @property
    def persons(self):
        addressbook = zope.component.hooks.getSite()
        session = icemac.addressbook.browser.base.get_session(self.request)
        return [addressbook[id] for id in session['person_ids']]

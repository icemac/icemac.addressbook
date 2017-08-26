from icemac.addressbook.i18n import _
import icemac.addressbook.browser.menus.menu
import icemac.addressbook.browser.search.result.handler.base
import icemac.addressbook.interfaces


class MailTo(icemac.addressbook.browser.search.result.handler.base.Base):
    """Create a mailto link for all persons in selection."""

    title = _('Send an e-mail')

    @property
    def unique_mail_addresses(self):
        addresses = set()
        for person in self.persons:
            email = icemac.addressbook.interfaces.IEMailAddress(person, None)
            if email is None:
                continue
            if not email.email:
                continue
            addresses.add(email.email)
        return sorted(addresses)

    def mailto_link(self):
        return 'mailto:?bcc=%s' % ','.join(self.unique_mail_addresses)


mailto = icemac.addressbook.browser.menus.menu.SelectMenuItemOn(
    'mailto.html')

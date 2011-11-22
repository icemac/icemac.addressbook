import icemac.addressbook.browser.base
import zope.component.hooks


class MailTo(object):

    def get_persons(self):
        addressbook = zope.component.hooks.getSite()
        session = icemac.addressbook.browser.base.get_session(self.request)
        for id in session['person_ids']:
            yield addressbook[id]

    @property
    def unique_mail_addresses(self):
        addresses = set()
        for person in self.get_persons():
            email = icemac.addressbook.interfaces.IEMailAddress(person, None)
            if email is None:
                continue
            if not email.email:
                continue
            addresses.add(email.email)
        return sorted(addresses)

    def mailto_link(self):
        return 'mailto:?bcc=%s' % ','.join(self.unique_mail_addresses)

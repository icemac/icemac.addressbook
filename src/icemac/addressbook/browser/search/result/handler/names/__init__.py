import icemac.addressbook.browser.base
import icemac.addressbook.browser.search.result.handler.base


class Names(icemac.addressbook.browser.search.result.handler.base.Base,
            icemac.addressbook.browser.base.BaseView):
    """Comma separed list of person names."""

    def person_list(self):
        return ', '.join(
            icemac.addressbook.interfaces.IPersonName(person).get_name()
            for person in self.persons)

    def next_url(self):
        return self.url(self.context)

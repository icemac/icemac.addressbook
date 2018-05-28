from icemac.addressbook.i18n import _
import icemac.addressbook.browser.base
import icemac.addressbook.browser.menus.menu
import icemac.addressbook.browser.search.result.handler.base


class Names(icemac.addressbook.browser.search.result.handler.base.Base,
            icemac.addressbook.browser.base.BaseView):
    """Comma separed list of person names."""

    title = _('Name list')

    def person_list(self):
        return ', '.join(
            icemac.addressbook.interfaces.IPersonName(person).get_name()
            for person in self.persons)

    def person_count(self):
        return len(self.persons)


names = icemac.addressbook.browser.menus.menu.SelectMenuItemOn(
    'person-names.html')

import icemac.addressbook.browser.base
import icemac.addressbook.browser.menus.menu
import icemac.addressbook.browser.search.result.handler.base


class Checklist(icemac.addressbook.browser.search.result.handler.base.Base,
                icemac.addressbook.browser.base.BaseView):
    """Check-list with person names."""

    def person_list(self):
        for person in self.persons:
            name = icemac.addressbook.interfaces.IPersonName(person).get_name()
            yield {'name': name,
                   'id': person.__name__}

    def person_count(self):
        return len(self.persons)


checklist = icemac.addressbook.browser.menus.menu.SelectMenuItemOn(
    'person-checklist.html')

from icemac.addressbook.i18n import _
import icemac.addressbook.browser.base
import icemac.addressbook.browser.menus.menu
import icemac.addressbook.browser.search.result.handler.base
import zope.cachedescriptors.property


class Birthdays(icemac.addressbook.browser.search.result.handler.base.Base,
                icemac.addressbook.browser.base.BaseView):
    """List of person names sorted by birthday."""

    title = _('Birthday list')

    @zope.cachedescriptors.property.Lazy
    def persons_with_birthday(self):
        return [x
                for x in self.persons
                if x.birth_date]

    def person_list(self):
        data = sorted((x.birth_date.month,
                       x.birth_date.day,
                       x.birth_date.year,
                       x)
                      for x in self.persons_with_birthday)
        formatter = self.request.locale.dates.getFormatter('date', 'medium')
        return ({
            'name': icemac.addressbook.interfaces.IPersonName(x[3]).get_name(),
            'birth_date': formatter.format(x[3].birth_date)
        } for x in data)

    def person_count(self):
        return len(self.persons_with_birthday)


birthdays = icemac.addressbook.browser.menus.menu.SelectMenuItemOn(
    'person-birthdays.html')

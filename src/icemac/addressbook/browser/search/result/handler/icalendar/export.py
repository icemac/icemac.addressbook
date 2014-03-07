from ..base import Base
from icemac.addressbook.browser.person.interfaces import IBirthDate
from icemac.addressbook.i18n import _
import icemac.addressbook.icalendar
import icemac.addressbook.interfaces
import zope.component
import zope.i18n


class iCalendar(Base):
    """Export birthdays of selected persons as iCalendar file."""

    def __call__(self):
        icemac.addressbook.icalendar.set_download_request_headers(
            self.request, 'birthdays')
        exporter = Exporter(self.persons, self.request)
        return exporter()


class Exporter(object):

    def __init__(self, persons, request):
        self.persons = persons
        self.request = request
        ab_title = icemac.addressbook.interfaces.IAddressBook(None).title
        message_id = _('birthdays of ${address_book}',
                       mapping={'address_book': ab_title})
        cal_name = zope.i18n.translate(message_id, context=self.request)
        # x-wr-calname is the calendar name used by Apple's iCal
        self.calendar = icemac.addressbook.icalendar.Calendar(
            **{'x-wr-calname': cal_name})

    def update(self):
        for person in self.persons:
            birthdate_data = zope.component.getMultiAdapter(
                (person, self.request), IBirthDate)
            event = birthdate_data.icalendar_event
            if event:
                self.calendar.add_component(event)

    def __call__(self):
        self.update()
        return self.calendar.to_ical()

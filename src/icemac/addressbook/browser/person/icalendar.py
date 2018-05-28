from __future__ import absolute_import
from .interfaces import IBirthDate
from datetime import timedelta
import icalendar
import icemac.addressbook.browser.base
import icemac.addressbook.interfaces
import zope.interface
import icemac.addressbook.icalendar


ONE_DAY = timedelta(days=1)


@zope.interface.implementer(IBirthDate)
class iCalendar(icemac.addressbook.browser.base.BaseView):
    """Render the person's birthdate as iCal file."""

    def __init__(self, context, request):
        # We need this contructor because this class is registered both as
        # browser:page and adapter!
        self.context = context
        self.request = request

    @property
    def icalendar_event(self):
        if self.context.birth_date is None:
            return
        summary = '%s (*%s)' % (
            icemac.addressbook.interfaces.ITitle(self.context),
            self.context.birth_date.year)
        return icalendar.Event(
            uid=self.url(self.context, 'iCalendar'),
            summary=summary,
            dtstart=icalendar.vDate(self.context.birth_date),
            dtend=icalendar.vDate(self.context.birth_date + ONE_DAY),
            rrule=icalendar.vRecur(freq='yearly')
        )

    def __call__(self):
        icemac.addressbook.icalendar.set_download_request_headers(
            self.request, 'birthday')
        cal = icemac.addressbook.icalendar.Calendar()
        cal.add_component(self.icalendar_event)
        return cal.to_ical()

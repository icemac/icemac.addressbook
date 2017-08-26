from icemac.addressbook.i18n import _
from .interfaces import IBirthDate
import icemac.addressbook.browser.base
import zope.component


class ExportList(icemac.addressbook.browser.base.BaseView):
    """List available export formats."""

    title = _('Export person data')

    def exporters(self):
        """Iterable of exporters having enough data so export something."""
        # XXX: This has no API, the exporters should be subscription adapters
        #      which return None if they have not enough data to export
        #      something and a dict consting of title and URL otherwise.
        birthdate_data = zope.component.getMultiAdapter(
            (self.context, self.request), IBirthDate)
        if birthdate_data.icalendar_event is not None:
            yield dict(title=_('iCalendar export of birth date (.ics file)'),
                       url=self.url(self.context, 'iCalendar'))

    def back_url(self):
        return self.url(self.context)
